import streamlit as st
import hashlib
import pandas as pd
from dna.parser import parse_upload
from dna.engine import load_traits, interpret, CAT_ICONS
from dna.presentation import plain_result
from dna.result_context import genotype_comparison, numeric_context
from dna.deep_explanations import detailed_explanation
from dna.trait_geography import genotype_alleles, frequency_summary, frequency_explanation
from dna.geography import fetch_frequencies
from dna.faq import CATEGORIES as FAQ_CATEGORIES, search_faq
from dna.highlights import build_highlights
from dna.origins_view import make_map_rows, make_support_rows
from dna.auto_origins import run_auto_comparison

st.set_page_config(page_title='Helix Explorer | DNA Explorer', page_icon='🧬', layout='wide')
st.markdown('''<style>.block-container{max-width:1150px;padding-top:2rem} .small-note{color:#777;font-size:.85rem}</style>''', unsafe_allow_html=True)
TRAITS = load_traits()
st.title('🧬 Helix Explorer')
st.caption('Understand the science behind your DNA — research and education, not medical diagnosis.')
st.warning('**Research-only tool.** Raw consumer DNA is not clinical-grade testing. Health results are not diagnoses, carrier-screening results, or medication advice. Never change medical care based on this app.')

with st.sidebar:
    st.header('Your DNA file')
    st.caption('**Public beta:** uploads are processed on the hosting server, not exclusively in your browser. Only upload your own DNA or data you are authorized to analyze.')
    consent = st.checkbox(
        'I understand this is research-only, and I consent to processing my uploaded DNA on the hosting server for this session.',
        key='dna_consent',
    )
    uploaded = st.file_uploader(
        'Upload AncestryDNA TXT or ZIP', type=['txt', 'tsv', 'zip'],
        disabled=not consent,
        help='Files are processed in server memory; no permanent storage is intentionally implemented. Do not upload if you need a guaranteed zero-retention service.',
        key='dna_file',
    )
    if st.button('Clear my DNA and restart', use_container_width=True):
        for key in list(st.session_state):
            if key.startswith('trait_geo_'):
                st.session_state.pop(key, None)
        for key in ('calls', 'stats', 'upload_identity', 'dna_file', 'dna_consent', 'geography_result', 'ancestry_result', 'ancestry_reference_identity'):
            st.session_state.pop(key, None)
        st.rerun()
    st.caption('No user database or intentional raw-DNA disk storage. Uploaded bytes and parsed genotypes may remain in Streamlit session/server memory until cleared or the session expires. Hosting-provider retention is outside this app’s control.')

if uploaded is not None and consent:
    # Hash for change detection; never display or log the uploaded content or digest.
    raw = uploaded.getvalue()
    identity = (uploaded.name, len(raw), hashlib.sha256(raw).hexdigest())
    if st.session_state.get('upload_identity') != identity:
        try:
            calls, stats = parse_upload(raw, uploaded.name)
            st.session_state['calls'] = calls
            st.session_state['stats'] = dict(stats)
            st.session_state['upload_identity'] = identity
            for key in list(st.session_state):
                if key.startswith('trait_geo_'):
                    st.session_state.pop(key, None)
        except (ValueError, OSError, UnicodeError) as exc:
            for key in ('calls', 'stats', 'upload_identity'):
                st.session_state.pop(key, None)
            st.error(f'Could not read DNA file: {exc}')
            st.stop()
    del raw
else:
    for key in ('calls', 'stats', 'upload_identity'):
        st.session_state.pop(key, None)

calls = st.session_state.get('calls', {})
if calls:
    stats = st.session_state['stats']
    a,b,c = st.columns(3)
    a.metric('Records read', f"{stats.get('records',0):,}")
    b.metric('Usable SNP calls', f"{stats.get('called',0):,}")
    c.metric('Call rate', f"{stats.get('called',0)/max(1,stats.get('records',0))*100:.1f}%")
    if stats.get('special_encoding'):
        st.info(f"{stats['special_encoding']:,} non-ACGT encoded records were skipped; insertion/deletion calls need special interpretation.")
else:
    st.info('To explore your own results, read the upload notice, check the consent box, and upload your AncestryDNA file. You can also browse the educational library without uploading.')

category_list = list(CAT_ICONS)
page = st.radio('Explore', ['My Genetic Highlights', 'Genetic Origins & Population History', 'Trait browser', 'Gene & variant search', 'FAQ', 'About & privacy'], horizontal=True)


def show_personal_context(trait, result):
    """Explain alternatives and numerical limits next to each interpreted finding."""
    rows = genotype_comparison(trait, result)
    if not rows:
        return
    st.markdown('**How your genotype compares with the alternatives**')
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.markdown('**What can we say about percentages?**')
    st.write(numeric_context(trait))
    st.caption('Genotypes are shown in the allele orientation used by this app. These are associations, not guarantees.')

def show_deep_explanation(trait, result):
    """Consistent educational explanations for every trait in every result view."""
    info = detailed_explanation(trait, result)
    st.markdown('**🧠 What this means for you**')
    st.write(info['takeaway'])
    st.markdown('**What is this gene actually doing?**')
    st.write(info['biology'])
    st.markdown('**Why does it matter in everyday life?**')
    st.write(info['importance'])
    st.markdown('**Practical takeaway**')
    st.write(info['action'])
    with st.expander('🧬 Compare other genotypes and understand the numbers'):
        if info['alternatives']:
            st.dataframe(pd.DataFrame(info['alternatives']), hide_index=True, use_container_width=True)
        else:
            st.write('This research marker has no reviewed genotype-by-genotype comparison. ' 
                     'Different DNA letters are not automatically different health outcomes.')
        st.markdown('**Can we put a percentage on it?**')
        st.write(numeric_context(trait))
        st.caption('Reference-population frequencies, when available in the geographic section, '
                   'measure how common an allele is—not your chance of experiencing a trait.')
    if trait['category'] == 'Health Genetics':
        st.warning('Raw consumer DNA cannot confirm or exclude a medical condition. '
                   'Confirm potentially important findings with an accredited clinical laboratory.')


@st.cache_data(ttl=86400, show_spinner=False)
def cached_trait_frequencies(rsid, allele):
    # Public variant identifier only; never send uploaded genotype or file.
    return fetch_frequencies(rsid, allele)


def show_trait_geography(trait, result):
    """Optional, sourced reference-frequency map in individual result cards."""
    alleles = genotype_alleles(result.get('genotype'))
    rsid = str(trait.get('rsid', ''))
    if not alleles or not rsid.startswith('rs'):
        return
    with st.expander('🌍 Where is this genetic variation found?'):
        st.write('Explore how often a DNA letter from your result appears in studied reference populations. '
                 'This is **population context**, not a test of where your ancestors came from.')
        selected = st.selectbox('DNA letter to compare', alleles, key=f"geo_allele_{trait['id']}",
                                help='If your genotype has two different letters, you can compare either one.')
        st.caption(f"Your genotype: {result['genotype']} · Variant: {rsid} · Selected letter: {selected}")
        if st.button('Show population frequencies and map', key=f"geo_fetch_{trait['id']}"):
            with st.spinner('Loading published reference-population data…'):
                try:
                    rows = cached_trait_frequencies(rsid, selected)
                    st.session_state[f"trait_geo_{trait['id']}"] = (selected, rows)
                except (RuntimeError, ValueError) as exc:
                    st.warning(str(exc))
        saved = st.session_state.get(f"trait_geo_{trait['id']}")
        if saved and saved[0] == selected:
            rows = frequency_summary(saved[1])
            if not rows:
                st.info('No compatible reference-population frequency data was returned for this DNA letter.')
                return
            st.markdown('**Where this allele is more common in the sampled populations**')
            st.write(frequency_explanation(selected, result['genotype'], rows))
            plot = pd.DataFrame(rows)
            st.bar_chart(plot.set_index('Population')['Frequency (%)'], horizontal=True)
            st.markdown('**Reference sample locations**')
            st.caption('Dots mark approximate locations associated with sampled populations, not the origins of this allele. '
                       'Some populations were sampled outside their ancestral region.')
            st.map(plot.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})[['lat', 'lon']])
            with st.expander('View percentages, population names, and data source'):
                st.dataframe(plot[['Population', 'Region', 'Frequency (%)', 'Source']],
                             hide_index=True, use_container_width=True)
            st.caption('Source: Ensembl variation API / 1000 Genomes Phase 3, when available. '
                       'Frequencies are allele frequencies, not genotype frequencies or trait probabilities. '
                       'Only the public rsID is requested; your DNA file is not sent to Ensembl.')


if page == 'My Genetic Highlights':
    st.subheader('⭐ My Genetic Highlights')
    st.caption('Prioritized, genotype-specific educational findings. These are not ranked by health importance, rarity, or medical risk.')
    if not calls:
        st.info('Upload your DNA to see your personalized highlights. The full educational library remains available in Trait browser.')
    else:
        highlights, exploratory, unavailable = build_highlights(TRAITS, calls)
        a,b,c = st.columns(3)
        a.metric('Interpretable highlights', len(highlights))
        b.metric('Other / exploratory markers', len(exploratory))
        c.metric('Missing / uninterpretable', len(unavailable))
        if not highlights:
            st.info('No reviewed personalized highlights found in the current small library. This does not imply anything about your health.')
        for item in highlights:
            t, r, v = item['trait'], item['result'], item['view']
            with st.container(border=True):
                st.markdown(f"**{CAT_ICONS[t['category']]} {v['name']}** · {t['evidence']}")
                st.markdown(f"### {v['headline']}")
                st.write(v['meaning'])
                st.markdown('**What this means in everyday life**')
                st.write(v['everyday'][0])
                st.caption(v['everyday'][1])
                show_deep_explanation(t, r)
                show_personal_context(t, r)
                show_trait_geography(t, r)
                if t['category'] == 'Health Genetics':
                    st.warning('Unconfirmed raw-array finding. Use clinical testing and genetic counseling for medical or reproductive decisions.')
                with st.expander('Why this matters / DNA details'):
                    st.write(v['intro'])
                    st.write(v['context'])
                    st.write(f"**{t['gene']} · {t['rsid']} · Genotype {r['genotype']}**")
                    st.link_button('Scientific reference', t['source'])
        with st.expander(f'Other research markers ({len(exploratory)})'):
            st.write('These genotypes are available, but they are not validated personalized highlights. A marker being present is not itself an important finding.')
            for item in exploratory:
                st.write(f"{item['trait']['gene']} · {item['trait']['title']} · {item['result']['status']}")
        with st.expander(f'Not tested / not interpretable ({len(unavailable)})'):
            for item in unavailable:
                st.write(f"{item['trait']['gene']} · {item['trait']['rsid']} · {item['result']['status']}")

elif page == 'Genetic Origins & Population History':
    st.subheader('🌍 Your Genetic Origins')
    st.markdown('### Where does your DNA resemble reference populations?')
    st.write('Explore how **many markers together** compare with people in published reference datasets. This is an early research comparison—not a family-tree map or an ancestry-percentage test.')
    st.info('**How to read this page:** A stronger match means the DNA markers analyzed fit that reference sample better than the other samples tested. It does not prove that your ancestors lived there.')
    if not calls:
        st.info('Upload your AncestryDNA file in the sidebar. No additional uploads are needed.')
    elif st.button('🌐 Explore my population matches', type='primary', use_container_width=True):
        with st.spinner('Collecting public reference data and comparing DNA markers…'):
            try:
                result = run_auto_comparison(calls)
                st.session_state['ancestry_result'] = result
                st.session_state['ancestry_reference_identity'] = st.session_state.get('upload_identity')
            except ValueError as exc:
                st.session_state.pop('ancestry_result', None)
                st.error(str(exc))
            except Exception:
                st.session_state.pop('ancestry_result', None)
                st.error('The public reference lookup could not finish. Try again later; no extra file is needed.')
    result = st.session_state.get('ancestry_result') if calls and st.session_state.get('ancestry_reference_identity') == st.session_state.get('upload_identity') else None
    if result:
        support = make_support_rows(result['rows'])
        map_rows = make_map_rows(result['rows'])
        st.divider()
        first, second, third = st.columns(3)
        first.metric('DNA markers compared', f"{result['markers']:,}")
        second.metric('Reference populations', result['population_count'])
        third.metric('Highest-ranking sample', result['rows'][0]['Population'])
        st.markdown('### 🗺️ Population comparison map')
        st.write('Each circle shows the **approximate geographic association of a reference population**, not your ancestral hometown. Larger circles mean that population ranked first more often when the same DNA markers were resampled.')
        if map_rows:
            frame = pd.DataFrame(map_rows)
            st.map(frame, latitude='lat', longitude='lon', size='marker_size', zoom=1, use_container_width=True)
            st.caption('Some reference participants were recruited outside their ancestral region. Map positions are illustrative regional anchors, not precise ancestral coordinates.')
        else:
            st.info('Geographic coordinates were not available for the returned reference populations.')
        st.markdown('### 📊 Which reference samples ranked most consistently?')
        st.write('The percentages below are **repeat-ranking percentages**, NOT percentages of your ancestry. For example, 70% means a population came first in 70% of repeated marker samples—not that 70% of your ancestors came from there.')
        chart = pd.DataFrame(support)
        st.bar_chart(chart.set_index('Population')['Top-rank consistency (%)'], horizontal=True)
        st.dataframe(chart, hide_index=True, use_container_width=True,
                     column_config={'Top-rank consistency (%)': st.column_config.NumberColumn(format='%.1f%%')})
        st.markdown('### What does this suggest about me?')
        st.write(f"Among the populations compared, **{result['rows'][0]['Population']}** was the best-fitting single reference sample for these markers. That is a statistical match—not proof of ancestry from that location.")
        st.warning('**Why we are not showing an ancestry makeup pie chart:** The current model assumes one population at a time. It cannot separate mixed ancestry or estimate regional ancestry proportions. Converting its scores into a pie chart would invent percentages. A validated multi-population admixture model and a larger matched reference panel are required for that feature.')
        with st.expander('How reliable is this? Technical details and limitations'):
            st.write('The comparison uses widely spaced markers, published 1000 Genomes frequencies, and a simple genotype-likelihood model. Markers were sampled across the genome but were **not selected as a validated ancestry-informative panel**. Reference groups are incomplete and unevenly sampled; results can change with the panel and marker selection.')
            st.write('**Top-rank consistency:** the fraction of bootstrap resamples in which each population had the best score. It is not the probability of having ancestors from that population.')
            st.dataframe(pd.DataFrame(result['rows']), hide_index=True, use_container_width=True)
            st.caption(f"Requested {result['requested_markers']} rsIDs; {result['reference_markers']} had comparable data; {result['failed_batches']} API batches failed.")
        st.caption('Source: Ensembl GRCh37 / 1000 Genomes Phase 3 population frequencies. Only public rsIDs are sent to Ensembl; your uploaded genotypes are not sent. Results depend on the external service.')
    else:
        st.caption('The map appears after the reference comparison finishes. The app does not generate ancestry percentages without an appropriate validated model.')

elif page == 'Overview':
    st.subheader('Explore categories')
    cols = st.columns(3)
    for i, cat in enumerate(category_list):
        with cols[i%3]:
            with st.container(border=True):
                st.markdown(f"### {CAT_ICONS[cat]} {cat}")
                st.caption(f"{sum(t['category']==cat for t in TRAITS)} curated markers")
                st.write('Browse in **Trait browser** →')
    st.subheader('How results are interpreted')
    st.write('A detected SNP is compared to a small, explicitly curated set of allele interpretations. Missing variants are labeled **Not tested**, never **negative**. No ethnicity percentages, polygenic scores, or medical diagnoses are inferred.')

elif page == 'Trait browser':
    selected = st.selectbox('Category', ['All categories'] + category_list)
    filtered = [t for t in TRAITS if selected == 'All categories' or t['category']==selected]
    search = st.text_input('Search traits, genes or rsIDs')
    filtered = [t for t in filtered if search.lower() in ' '.join([t['title'], t['gene'], t['rsid']]).lower()]
    st.caption(f'{len(filtered)} curated traits / markers')
    for t in filtered:
        result = interpret(t, calls) if calls else {'status':'Upload to personalize','genotype':'—','meaning':'No file uploaded.'}
        view = plain_result(t, result, bool(calls))
        with st.expander(f"{CAT_ICONS[t['category']]} {view['name']}"):
            st.markdown(f"### {view['headline']}")
            st.write(view['meaning'])
            st.markdown('**In plain English**')
            st.write(view['everyday'][0])
            st.caption(view['everyday'][1])
            show_deep_explanation(t, result)
            show_personal_context(t, result)
            show_trait_geography(t, result)
            if calls:
                st.caption(f"Your genotype: {result['genotype']} · Evidence: {t['evidence']}")
            st.markdown('**What does this gene do?**')
            st.write(view['intro'])
            st.markdown('**Why does it matter?**')
            st.write(view['context'])
            if t['category'] == 'Health Genetics':
                st.caption('Health information: consumer raw DNA cannot confirm or exclude a diagnosis, carrier status, or personal disease risk. Use clinical testing for medical decisions.')
            with st.expander('See the DNA details and scientific source'):
                if t.get('variant_name'):
                    st.write(f"**Specific mutation:** {t['variant_name']} ({t.get('variant_protein', '')})")
                    st.write(f"**DNA change:** {t.get('variant_hgvs', '')} · **Classification:** {t.get('clinical_classification', '')}")
                st.write(f"Gene: **{t['gene']}** · Marker: **{t['rsid']}** · Your genotype: **{result['genotype']}**")
                st.write(f"Evidence: {t['evidence']}")
                st.write(f"Important limitations: {t['caveat']}")
                st.link_button('Open scientific reference', t['source'])

elif page == 'Gene & variant search':
    query = st.text_input('Enter gene symbol or rsID', placeholder='e.g., CFTR or rs80034486')
    matches = [t for t in TRAITS if query and query.lower() in (t['gene']+' '+t['rsid']+' '+t['title']).lower()]
    if matches:
        for t in matches:
            r = interpret(t, calls) if calls else {'genotype':'—','status':'Upload to personalize','meaning':'No file uploaded.'}
            view = plain_result(t, r, bool(calls))
            with st.container(border=True):
                st.subheader(view['name'])
                st.markdown(f"**{view['headline']}**")
                st.write(view['meaning'])
                st.markdown('**In plain English**')
                st.write(view['everyday'][0])
                st.caption(view['everyday'][1])
                show_deep_explanation(t, r)
                show_personal_context(t, r)
                show_trait_geography(t, r)
                if calls:
                    st.caption(f"Your genotype: {r['genotype']} · Evidence: {t['evidence']}")
                if t.get('variant_name'):
                    st.info(f"**Identified mutation: {t['variant_name']}** ({t.get('variant_protein', '')}). This means one amino acid in the CFTR protein changes from asparagine (N) to lysine (K) at position 1303. The variant is classified as disease-causing, but your consumer DNA call needs clinical confirmation.")
                st.write(view['intro'])
                st.caption(view['context'])
                with st.expander('Technical details and reference'):
                    if t.get('variant_name'):
                        st.write(f"**Mutation:** {t['variant_name']} ({t.get('variant_protein', '')})")
                        st.write(f"**DNA change:** {t.get('variant_hgvs', '')}")
                        st.write(f"**Clinical classification of this variant:** {t.get('clinical_classification', '')}")
                        st.write(f"**Reference / variant alleles:** {t.get('reference_allele', '')} / {t.get('alternate_allele', '')} · **Genome build:** {t.get('reference_build', '')}")
                    st.write(f"Gene: {t['gene']} · Marker: {t['rsid']} · Genotype: {r['genotype']}")
                    st.write(t['caveat'])
                    st.link_button('Scientific reference',t['source'])
    elif query:
        st.info('Not in the curated library yet. This does not mean the variant is absent from your DNA file.')
    if calls:
        st.divider()
        st.subheader('Exact raw rsID lookup')
        rs = st.text_input('Look up any rsID in your uploaded file', placeholder='rs123456')
        if rs:
            call = calls.get(rs.strip())
            if call:
                st.write(f"**{rs}:** {call['genotype']} · chromosome {call['chromosome']} · position {call['position']} (as reported in file)")
                st.caption('Raw genotype only. No automatic medical or trait interpretation.')
            else:
                st.write('Not found or no usable call. This is not a negative clinical test.')

elif page == 'FAQ':
    st.subheader('Frequently asked questions')
    st.write('New to genetics? Start here. These answers explain the terms you see throughout Helix Explorer. You can read them without uploading DNA.')
    faq_query = st.text_input('Search common questions', placeholder='Try: allele, genotype, carrier, privacy…', key='faq_search')
    faq_category = st.selectbox('Browse FAQ topics', ['All topics'] + FAQ_CATEGORIES, key='faq_category')
    faq_results = search_faq(faq_category, faq_query)
    st.caption(f'{len(faq_results)} questions')
    if not faq_results:
        st.info('No matching questions. Try a different search term or select All topics.')
    for topic, question, answer in faq_results:
        with st.expander(question):
            st.write(answer)
            st.caption(f'Topic: {topic}')
    st.divider()
    st.info('Educational information only. A genetic counselor or qualified clinician can help interpret clinical findings.')

else:
    st.subheader('Privacy and limitations')
    st.write('**Public upload beta:** files are transmitted to the Streamlit hosting server over HTTPS when deployed with HTTPS. This app does not intentionally save raw DNA to a database, write uploads to disk, send genotypes to an AI API, or create accounts. Streamlit retains upload bytes and parsed genotypes in server/session memory, potentially until session expiry. Clearing your profile removes app session references but cannot guarantee immediate memory erasure or control provider backups, logs, or telemetry. Do not upload another person’s DNA without authorization.')
    st.write('Only AncestryDNA-style tab-delimited files are supported. Calls with insertion/deletion encodings are skipped. Genome build, allele strand, variant annotation, and source citations must be validated before interpreting new markers.')
    st.write('The knowledge base is intentionally small and illustrative. A marker not tested, or not included in this library, does not indicate a normal result. Confirm any potentially important result with a qualified clinician and accredited laboratory.')
    st.write('Genetic Origins offers an experimental, automatic multi-marker population comparison using public reference frequencies; it is not validated ancestry inference. No ancestry percentages, risk scores, drug dosing, or comprehensive carrier screening are provided.')

if calls:
    st.divider()
    rows=[]
    for t in TRAITS:
        r=interpret(t,calls)
        rows.append({'Category':t['category'],'Trait':t['title'],'Gene':t['gene'],'rsID':t['rsid'],'Genotype':r['genotype'],'Status':r['status'],'Interpretation':plain_result(t,r,True)['meaning'],'Headline':plain_result(t,r,True)['headline'],'Evidence':t['evidence'],'Caveat':t['caveat'],'Source':t['source']})
    st.download_button('Download curated results (CSV)',pd.DataFrame(rows).to_csv(index=False).encode('utf-8'),'dna_explorer_results.csv','text/csv')
    st.caption('Downloaded report contains sensitive personal genotype information. Store securely.')

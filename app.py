import streamlit as st
import hashlib
import pandas as pd
from dna.parser import parse_upload
from dna.engine import load_traits, interpret, CAT_ICONS
from dna.presentation import plain_result
from dna.faq import CATEGORIES as FAQ_CATEGORIES, search_faq
from dna.highlights import build_highlights
from dna.geography import fetch_frequencies
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
    st.subheader('🌍 Genetic Origins & Population History')
    st.markdown('### Compare your whole DNA profile with reference populations')
    st.write('This research feature combines **at least 30 independent genetic markers** against population allele frequencies. It reports **relative statistical similarity**, not ancestry percentages, ethnicity, geographic exposure, or family origin.')
    st.warning('**Experimental method, not a validated ancestry test.** Results depend strongly on the reference panel and populations included. Mixed ancestry, unequal sampling, genetic linkage and other effects can distort the rankings. Do not interpret the leading population as your origin.')
    st.write('**Only your AncestryDNA file is needed.** Click the button below to automatically retrieve published population frequencies for multiple markers. The app sends selected public **rsIDs**, not your DNA letters or uploaded file, to Ensembl. The reference service must be online.')
    st.info('**What this can tell you:** which reference samples best fit the selected markers in this limited experiment. **What it cannot tell you:** ancestry percentages, your ethnicity, exact ancestral locations, or where you have lived. This is not a validated ancestry test, and the markers are not a curated ancestry-informative panel.')
    if not calls:
        st.info('Upload your AncestryDNA file in the sidebar to enable the automatic comparison.')
    elif st.button('Compare my DNA with reference populations', type='primary'):
        with st.spinner('Requesting public reference frequencies and comparing markers. This may take a minute…'):
            try:
                result = run_auto_comparison(calls)
                st.session_state['ancestry_result'] = result
                st.session_state['ancestry_reference_identity'] = st.session_state.get('upload_identity')
            except ValueError as exc:
                st.session_state.pop('ancestry_result', None)
                st.error(str(exc))
            except Exception:
                st.session_state.pop('ancestry_result', None)
                st.error('Could not complete the public reference lookup. Please retry later; no additional file upload is needed.')
    result = st.session_state.get('ancestry_result') if st.session_state.get('ancestry_reference_identity') == st.session_state.get('upload_identity') and calls else None
    if result:
        st.success(f"Compared {result['markers']} widely spaced SNPs across {result['population_count']} reference samples.")
        st.markdown('### Closest statistical matches in this reference panel')
        best = result['rows'][0]
        st.write(f"**Closest match in this experiment:** {best['Population']}. This does **not** mean your ancestry comes from that population. It means this reference sample best fits the selected markers among those compared.")
        st.dataframe(pd.DataFrame(result['rows']), hide_index=True, use_container_width=True)
        st.bar_chart(pd.DataFrame(result['rows']).set_index('Population')['Relative log-likelihood'], horizontal=True)
        st.markdown('**Understanding the numbers**')
        st.write('**Relative log-likelihood:** 0 marks the best-fitting population in this comparison; more negative values fit worse. These are not percentages. **Bootstrap top-rank frequency:** how often a population came first when markers were randomly resampled; it is not your probability of having ancestry from that group.')
        st.caption(f"Requested {result['requested_markers']} public marker identifiers; {result['reference_markers']} had comparable reference data. Unavailable API batches: {result['failed_batches']}.")
        st.warning('The method assumes one reference population and cannot model mixed ancestry. Reference samples are limited, and randomly selected genome-wide SNPs are not a validated ancestry panel. Do not use these rankings to infer ethnicity, nationality, or personal geographic exposure.')
    st.caption('Reference: Ensembl GRCh37 REST API, 1000 Genomes Phase 3 allele frequencies. The analysis only runs on request. A service outage or insufficient matched data yields no result rather than invented estimates.')
    st.divider()
    with st.expander('Research explorer: frequencies for one marker (not your ancestry)'):
        st.caption('The tool below is for learning about one marker. It is not used to calculate geographic origins.')
    st.divider()
    st.markdown('### Individual-marker population frequencies (educational)')
    st.write('Explore **how common an individual DNA letter is in reference samples** from different populations. This is NOT a map of your ancestry, ethnicity, birthplace, or family origin.')
    st.caption('Population frequencies are requested from the public Ensembl API only after you click Load. The app sends the selected rsID, not your uploaded DNA or genotype.')
    candidates = [t for t in TRAITS if t.get('rsid', '').startswith('rs')]
    selected = st.selectbox('Select a variant', candidates, format_func=lambda t: f"{t['title']} · {t['gene']} · {t['rsid']}")
    genotype = calls.get(selected['rsid'], {}).get('genotype') if calls else None
    if genotype:
        st.write(f"Your uploaded genotype: **{genotype}**. This is shown locally and is not sent to Ensembl.")
    allele = st.selectbox('DNA letter to compare across populations', ['A', 'C', 'G', 'T'], index=0)
    st.caption('Choose the allele intentionally. A variant may have multiple alleles, and a frequency for one letter is not a trait frequency.')
    if st.button('Load real reference population frequencies', type='primary'):
        with st.spinner('Fetching public reference frequencies…'):
            try:
                st.session_state['geography_result'] = {'rsid': selected['rsid'], 'allele': allele, 'rows': fetch_frequencies(selected['rsid'], allele)}
            except RuntimeError as exc:
                st.session_state.pop('geography_result', None)
                st.error(str(exc))
    geo = st.session_state.get('geography_result')
    if geo and geo['rsid'] == selected['rsid'] and geo['allele'] == allele:
        rows = geo['rows']
        if rows:
            frame = pd.DataFrame(rows)
            st.caption(f"{len(rows)} reference populations with reported frequency for allele {allele}. Missing populations are omitted, not treated as zero.")
            st.bar_chart(frame.set_index('Population')['Allele frequency'], horizontal=True)
            st.map(frame.rename(columns={'Latitude':'lat', 'Longitude':'lon'}), latitude='lat', longitude='lon', size=75)
            st.caption('Map pins indicate approximate reference sample collection/recruitment locations, not ancestral origins or individual locations. Some samples were recruited outside their population namesake.')
            st.dataframe(frame[['Population','Region','Allele frequency','Source']], hide_index=True, use_container_width=True, column_config={'Allele frequency': st.column_config.NumberColumn(format='%.3f')})
        else:
            st.info('No matching 1000 Genomes reference frequencies were returned for this allele. This is not evidence that it is absent from any population.')
        st.link_button('View reference variant in Ensembl', f"https://www.ensembl.org/Homo_sapiens/Variation/Explore?v={selected['rsid']}")
    st.info('**Important:** Reference populations are limited samples, not all residents of a region. Frequency differences do not establish ancestry, race, nationality, or a person’s geographic origin. Some variants have no comparable population data.')

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

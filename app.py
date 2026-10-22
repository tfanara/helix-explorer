import streamlit as st
import hashlib
import pandas as pd
from dna.parser import parse_upload
from dna.engine import load_traits, interpret, CAT_ICONS
from dna.presentation import plain_result
from dna.faq import CATEGORIES as FAQ_CATEGORIES, search_faq

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
        for key in ('calls', 'stats', 'upload_identity', 'dna_file', 'dna_consent'):
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
page = st.radio('Explore', ['Overview', 'Trait browser', 'Gene & variant search', 'FAQ', 'About & privacy'], horizontal=True)

if page == 'Overview':
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
    st.write('No ancestry inference, risk scores, drug dosing, or comprehensive carrier screening is provided.')

if calls:
    st.divider()
    rows=[]
    for t in TRAITS:
        r=interpret(t,calls)
        rows.append({'Category':t['category'],'Trait':t['title'],'Gene':t['gene'],'rsID':t['rsid'],'Genotype':r['genotype'],'Status':r['status'],'Interpretation':r['meaning'],'Evidence':t['evidence'],'Caveat':t['caveat'],'Source':t['source']})
    st.download_button('Download curated results (CSV)',pd.DataFrame(rows).to_csv(index=False).encode('utf-8'),'dna_explorer_results.csv','text/csv')
    st.caption('Downloaded report contains sensitive personal genotype information. Store securely.')

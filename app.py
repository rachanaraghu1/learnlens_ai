"""LearnLens AI — local learning analytics application."""
import random
import streamlit as st
import pandas as pd
import plotly.express as px
from config import SUBJECT, MODEL_PATH
from src.database.db import initialize
from src.database import repository as repo
from src.auth import authenticate, register_account, account_for_user, logout
from src.data.question_bank import topics
from src.analytics.mastery import calculate_mastery
from src.analytics.learning_patterns import accuracy_over_time
from src.analytics.knowledge_gaps import mistake_summary, performance_patterns
from src.analytics.adaptive import select_next_question
from src.recommendations.recommender import recommend_topics
from src.recommendations.study_plan import build_plan
from src.models.predict import load_model, predict_probability
from src.features.feature_engineering import build_features

st.set_page_config(page_title='LearnLens AI',page_icon='◉',layout='wide')
st.markdown('''<style>
.stApp{background:#f7fafc;color:#172b4d}.block-container{padding:1.2rem 2rem 3rem;max-width:1320px}.brand{font-size:1.25rem;font-weight:800;color:#102a43;letter-spacing:-.03em}.public-nav{border-bottom:1px solid #e7edf3;padding-bottom:.7rem;margin-bottom:1.4rem}.hero{padding:4rem 3.2rem;border-radius:26px;background:linear-gradient(120deg,#102a43 0%,#124b65 65%,#087e8b 100%);color:white;margin:.5rem 0 2rem;box-shadow:0 20px 50px #102a4322}.hero h1{color:white;margin:0;font-size:clamp(2.8rem,6vw,5rem);letter-spacing:-.055em;line-height:1.05}.hero p{color:#e1f4f5;font-size:1.15rem;max-width:620px;line-height:1.65;margin:1.1rem 0 0}.eyebrow{color:#13a9a4;font-weight:750;letter-spacing:.12em;text-transform:uppercase;font-size:.76rem}.feature-card{height:100%;background:white;border:1px solid #e4ebf2;border-radius:18px;padding:1.35rem;box-shadow:0 8px 28px #102a4309}.feature-card h3{color:#102a43;margin:.4rem 0}.feature-card p{color:#5c6f82;line-height:1.6}.section{padding:2.2rem 0}.footer{border-top:1px solid #e4ebf2;margin-top:3rem;padding:1.5rem 0;color:#62758a}.stButton>button[kind="primary"]{background:#087e8b;border-color:#087e8b;border-radius:10px;font-weight:700;padding:.6rem 1.2rem}.stButton>button{border-radius:10px}.stTextInput input{border-radius:10px}.stProgress>div>div{background:#087e8b}.stTabs [data-baseweb="tab"]{font-weight:650}.auth-card{max-width:560px;margin:1.2rem auto;background:#fff;border:1px solid #e4ebf2;border-radius:20px;padding:1.6rem 2rem;box-shadow:0 12px 40px #102a430c}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;height:0!important;visibility:hidden!important}
#MainMenu,footer{visibility:hidden}
[data-testid="stAppViewContainer"]>.main{padding-top:0!important}
.block-container{padding-top:1rem!important}
</style>''',unsafe_allow_html=True)
initialize()

def _clear_quiz_state():
    for key in ('quiz_id','quiz_student','quiz_mode','quiz_qids','quiz_index','quiz_started','quiz_feedback','quiz_done'):
        st.session_state.pop(key,None)

def _go_to_signup():
    st.session_state['public_nav']='Sign Up'

def render_feature_cards():
    st.markdown('<div class="section"><div class="eyebrow">A clearer way to learn</div><h2>From quiz scores to meaningful progress</h2><p>Every practice session becomes a useful signal for what to learn next.</p></div>',unsafe_allow_html=True)
    cards=[('01','Understand your strengths','See topic mastery, trends, response times, and recurring misconceptions in one place.'),('02','Practice at your pace','Take focused, mixed, weak-topic, and adaptive quizzes built from reviewed questions.'),('03','Know what to do next','Get transparent revision priorities and a practical study plan that responds to your results.'),('04','See how estimates work','Explore interpretable machine learning insights alongside clearly labeled rule-based advice.')]
    cols=st.columns(4)
    for col,(num,title,body) in zip(cols,cards):
        with col: st.markdown(f'<div class="feature-card"><div class="eyebrow">{num}</div><h3>{title}</h3><p>{body}</p></div>',unsafe_allow_html=True)

def render_footer():
    st.markdown('<div class="footer">LearnLens AI <span style="float:right">Understand how you learn. Discover what you don’t know.</span></div>',unsafe_allow_html=True)

current_user=None
if st.session_state.get('user_id'):
    current_user=account_for_user(st.session_state.user_id)
    if current_user is None:
        st.session_state.pop('user_id',None)
        _clear_quiz_state()

if current_user is None:
    nav_cols=st.columns([2.2,6.5,1,1.2])
    with nav_cols[0]: st.markdown('<div class="brand">◉ LearnLens AI</div>',unsafe_allow_html=True)
    with nav_cols[1]:
        public_nav=st.radio('Main navigation',['Home','Features','About','Login','Sign Up'],horizontal=True,key='public_nav',label_visibility='collapsed')
    st.markdown('<div class="public-nav"></div>',unsafe_allow_html=True)
    if public_nav=='Home':
        st.markdown('<div class="hero"><div class="eyebrow" style="color:#65d5d0">PERSONALIZED LEARNING ANALYTICS</div><h1>Your Learning.<br>In Focus.</h1><p>Turn every practice session into a clearer picture of what you know, what needs attention, and where to go next.</p></div>',unsafe_allow_html=True)
        st.button('Get Started',type='primary',on_click=_go_to_signup)
        render_feature_cards()
        st.markdown('<div class="section"><h2>Learning insight you can act on</h2><p>LearnLens combines explainable analytics, adaptive practice, and an honest view of machine learning estimates to make your next step easier to see.</p></div>',unsafe_allow_html=True)
        render_footer()
    elif public_nav=='Features':
        st.markdown('<div class="section"><div class="eyebrow">Platform features</div><h1>Make every attempt count.</h1><p>Explore a focused toolkit for understanding learning progress and planning what comes next.</p></div>',unsafe_allow_html=True)
        render_feature_cards(); render_footer()
    elif public_nav=='About':
        st.markdown('<div class="section"><div class="eyebrow">About LearnLens</div><h1>Learning insight with transparency built in.</h1><p>LearnLens AI is a local-first educational analytics application. It pairs a real supervised learning pipeline with transparent rule-based mastery and recommendation logic. Predictions are estimates, not judgments of a learner.</p></div>',unsafe_allow_html=True)
        render_feature_cards(); st.info('The current question library focuses on Computer Networks. Model training uses clearly labeled synthetic data and is not validated on real learners.'); render_footer()
    elif public_nav=='Sign Up':
        st.markdown('<div class="auth-card"><div class="eyebrow">Create your account</div><h1>Start learning in focus.</h1><p>Your learning history is private to your account.</p></div>',unsafe_allow_html=True)
        with st.form('signup_form'):
            full_name=st.text_input('Name',max_chars=80)
            email=st.text_input('Email',max_chars=254)
            username=st.text_input('Username',max_chars=32,help='3–32 letters, numbers, dots, underscores, or hyphens.')
            password=st.text_input('Password',type='password',max_chars=256,help='Use at least 10 characters.')
            confirm=st.text_input('Confirm password',type='password',max_chars=256)
            submitted=st.form_submit_button('Create account',type='primary',use_container_width=True)
        if submitted:
            try:
                account=register_account(full_name,email,username,password,confirm)
                _clear_quiz_state(); st.session_state.user_id=account['user_id']
                st.success('Account created. Your personal dashboard is ready.')
                st.rerun()
            except ValueError as exc: st.error(str(exc))
        render_footer()
    else:
        st.markdown('<div class="auth-card"><div class="eyebrow">Welcome back</div><h1>Log in to LearnLens.</h1><p>Continue with your own learning history and study plan.</p></div>',unsafe_allow_html=True)
        with st.form('login_form'):
            identifier=st.text_input('Username or email')
            password=st.text_input('Password',type='password')
            submitted=st.form_submit_button('Log in',type='primary',use_container_width=True)
        if submitted:
            account=authenticate(identifier,password)
            if account:
                _clear_quiz_state(); st.session_state.user_id=account['user_id']; st.rerun()
            st.error('We could not verify those credentials. Check your username/email and password.')
        render_footer()
    st.stop()

student_id=current_user['student_id']
st.sidebar.markdown('## ◉ LearnLens AI')
st.sidebar.caption('Understand how you learn. Discover what you don’t know.')
st.sidebar.markdown(f"**{current_user['student_name']}**")
page=st.sidebar.radio('Workspace',['Dashboard','Take a Quiz','Learning Analytics','Knowledge Gaps','Study Plan','ML Insights','About'])
st.sidebar.divider()
with st.sidebar.expander('Profile settings'):
    if st.button('Reset my learning history',help='Clears this account’s quiz attempts and study tasks while keeping the account.'):
        repo.clear_student(student_id); _clear_quiz_state(); st.rerun()
if st.sidebar.button('Log out',use_container_width=True):
    logout(st.session_state); st.rerun()

responses=repo.response_frame(student_id); sessions=repo.sessions_frame(student_id)
mastery=calculate_mastery(responses); recs=recommend_topics(mastery,responses); model=load_model()
def hero(title,desc): st.markdown(f'<div class="hero"><h1>{title}</h1><p>{desc}</p></div>',unsafe_allow_html=True)
def metric_row():
    complete=sessions[sessions.submitted==1] if not sessions.empty else sessions
    total=int(len(complete)); accuracy=float(responses.is_correct.mean()*100) if not responses.empty else 0
    mastered=int((mastery.mastery_score>=75).sum()) if not mastery.empty else 0; revise=int((mastery.mastery_score<60).sum()) if not mastery.empty else 0
    a,b,c,d=st.columns(4)
    for col,val,lab in [(a,total,'Quizzes completed'),(b,f'{accuracy:.0f}%', 'Overall accuracy'),(c,mastered,'Topics strong'),(d,revise,'Topics to revisit')]:
        col.metric(lab,val)

if page=='Dashboard':
    hero('Your learning, in focus',f'{SUBJECT} · Personalized learning analytics for {current_user["student_name"]}')
    metric_row(); left,right=st.columns([1.2,1])
    with left:
        st.subheader('Progress over time')
        trend=accuracy_over_time(responses)
        if trend.empty: st.info('Complete a quiz to see your progress here.')
        else: st.plotly_chart(px.line(trend,x='date',y='accuracy',markers=True,labels={'accuracy':'Accuracy (%)','date':'Date'},template='plotly_white'),use_container_width=True)
    with right:
        st.subheader('Topic mastery')
        if mastery.empty: st.info('Topic insights appear after your first quiz.')
        else: st.plotly_chart(px.bar(mastery.sort_values('mastery_score'),x='mastery_score',y='topic',orientation='h',color='mastery_score',color_continuous_scale=['#e8796f','#f0bd59','#2ba98a'],range_color=(0,100),labels={'mastery_score':'Mastery (%)','topic':''},template='plotly_white'),use_container_width=True)
    st.subheader('Recommended next step')
    if recs: st.info(f"Review **{recs[0]['topic']}**: {recs[0]['reason']}. Start with {recs[0]['suggested_difficulty'].lower()} practice.")
    else: st.info('Take a short quiz to generate a personal revision recommendation.')
    if not sessions.empty:
        st.subheader('Recent quiz history'); st.dataframe(sessions[['start_time','quiz_type','total_questions','submitted']].head(8),hide_index=True,use_container_width=True)

elif page=='Take a Quiz':
    hero('Practice with purpose','Choose a focus, answer at your pace, and review every explanation.')
    with st.expander('Start a quiz',expanded='quiz_id' not in st.session_state):
        mode=st.selectbox('Quiz mode',['Topic-based','Mixed-topic','Weak-topic practice','Adaptive practice'])
        topic=st.selectbox('Topic',topics(),disabled=mode=='Mixed-topic')
        difficulty=st.selectbox('Difficulty',['Any','Easy','Medium','Hard'])
        count=st.slider('Number of questions',3,15,5)
        if st.button('Start quiz',type='primary'):
            bank=repo.question_rows(); candidates=[q for q in bank if (mode=='Mixed-topic' or q['topic']==topic) and (difficulty=='Any' or q['difficulty']==difficulty)]
            if mode=='Weak-topic practice' and recs:
                weak={r['topic'] for r in recs[:3]}; candidates=[q for q in bank if q['topic'] in weak and (difficulty=='Any' or q['difficulty']==difficulty)]
            if mode=='Adaptive practice' and recs:
                weak={r['topic'] for r in recs[:4]}; candidates=[q for q in bank if q['topic'] in weak]
            if not candidates: st.error('No questions match these choices. Try another topic or difficulty.')
            else:
                chosen=random.sample(candidates,min(count,len(candidates)))
                session=repo.start_session(student_id,mode,len(chosen)); st.session_state.quiz_id=session; st.session_state.quiz_student=student_id; st.session_state.quiz_mode=mode; st.session_state.quiz_qids=[q['question_id'] for q in chosen]; st.session_state.quiz_index=0; st.session_state.quiz_started=pd.Timestamp.now().isoformat(); st.session_state.quiz_feedback={}; st.session_state.quiz_done=False; st.rerun()
    if st.session_state.get('quiz_id') and st.session_state.get('quiz_student')==student_id and not st.session_state.get('quiz_done'):
        bank={q['question_id']:q for q in repo.question_rows()}; qids=st.session_state.quiz_qids; ix=st.session_state.quiz_index
        q=bank[qids[ix]]; st.progress((ix+1)/len(qids),text=f"Question {ix+1} of {len(qids)}")
        st.markdown(f"### {q['question_text']}"); st.caption(f"{q['topic']} · {q['subtopic']} · {q['difficulty']} · about {q['estimated_time']} sec")
        previous=st.session_state.quiz_feedback.get(q['question_id']); already_answered=previous is not None
        selected=st.radio('Choose one answer',q['options'],index=None if not already_answered else 'ABCD'.index(previous['selected']),key=f"answer_{st.session_state.quiz_id}_{q['question_id']}",disabled=already_answered,format_func=lambda x:f"{('ABCD'[q['options'].index(x)])}. {x}")
        if not already_answered and st.button('Save answer',type='primary'):
            if selected is None: st.warning('Choose an answer before saving.')
            else:
                letter='ABCD'[q['options'].index(selected)]; seconds=(pd.Timestamp.now()-pd.Timestamp(st.session_state.quiz_started)).total_seconds()
                saved=repo.record_response(st.session_state.quiz_id,student_id,q['question_id'],letter,q['correct_answer'],seconds)
                is_correct=letter==q['correct_answer']
                st.session_state.quiz_feedback[q['question_id']]={'selected':letter,'correct':is_correct}
                # Replace the next adaptive item using the answer just given, current weakness priority,
                # and all questions already encountered; selection is a documented rule, not ML.
                if st.session_state.quiz_mode=='Adaptive practice' and ix+1<len(qids):
                    priority={r['topic']:r['priority'] for r in recs}
                    next_q=select_next_question(repo.question_rows(),qids[:ix+1],priority,[x['correct'] for x in st.session_state.quiz_feedback.values()],random.Random(ix+len(qids)))
                    if next_q:
                        old_next=qids[ix+1]; qids[ix+1]=next_q['question_id']
                        if next_q['question_id'] in qids[ix+2:]: qids[qids.index(next_q['question_id'],ix+2)]=old_next
                        st.session_state.quiz_qids=qids
                st.rerun()
        if already_answered:
            if previous['correct']: st.success('Correct!')
            else: st.error(f"Not quite. Correct answer: {q['correct_answer']}. {q['options']['ABCD'.index(q['correct_answer'])]}")
            st.info(q['explanation'])
        col1,col2,col3=st.columns([1,1,3])
        if col1.button('← Previous',disabled=ix==0): st.session_state.quiz_index-=1; st.rerun()
        if col2.button('Next →',disabled=ix>=len(qids)-1 or not already_answered): st.session_state.quiz_index+=1; st.session_state.quiz_started=pd.Timestamp.now().isoformat(); st.rerun()
        if ix==len(qids)-1 and len(st.session_state.quiz_feedback)==len(qids):
            if st.button('Submit quiz',type='primary'):
                repo.submit_session(st.session_state.quiz_id,student_id); st.session_state.quiz_done=True; st.rerun()
    elif st.session_state.get('quiz_done'):
        quiz_rows=st.session_state.quiz_feedback; score=sum(x['correct'] for x in quiz_rows.values()); st.success(f"Quiz complete — {score} of {len(quiz_rows)} correct ({score/len(quiz_rows)*100:.0f}%).")
        if st.button('Start another quiz'): st.session_state.pop('quiz_id',None); st.rerun()
        st.caption('Review topic analytics and recommendations for the next step.')

elif page=='Learning Analytics':
    hero('Learning analytics','Explore accuracy, response time, difficulty, and how your performance changes.')
    if responses.empty: st.info('Complete quizzes to unlock your learning analytics.')
    else:
        c1,c2=st.columns(2)
        with c1: st.subheader('Accuracy by topic'); st.plotly_chart(px.bar(responses.groupby('topic',as_index=False).is_correct.mean().assign(is_correct=lambda d:d.is_correct*100),x='topic',y='is_correct',labels={'is_correct':'Accuracy (%)','topic':''},template='plotly_white'),use_container_width=True)
        with c2: st.subheader('Performance by difficulty'); st.plotly_chart(px.bar(responses.groupby('difficulty',as_index=False).is_correct.mean().assign(is_correct=lambda d:d.is_correct*100),x='difficulty',y='is_correct',labels={'is_correct':'Accuracy (%)','difficulty':''},template='plotly_white'),use_container_width=True)
        st.subheader('Response time'); st.plotly_chart(px.box(responses,x='topic',y='time_taken_seconds',color='is_correct',labels={'time_taken_seconds':'Seconds','topic':'','is_correct':'Correct'},template='plotly_white'),use_container_width=True)
        st.subheader('Repeated mistakes'); st.dataframe(mistake_summary(responses),hide_index=True,use_container_width=True)
        for pattern in performance_patterns(responses): st.info(pattern)

elif page=='Knowledge Gaps':
    hero('Knowledge gaps','Mastery is an estimate. Sample size and recent practice affect confidence.')
    if mastery.empty: st.info('Answer a few questions to build topic-level evidence.')
    else:
        st.plotly_chart(px.imshow(mastery.set_index('topic')[['mastery_score']].T,aspect='auto',color_continuous_scale='RdYlGn',range_color=(0,100),labels={'x':'Topic','y':'Measure','color':'Mastery'},template='plotly_white'),use_container_width=True)
        st.dataframe(mastery[['topic','mastery_score','revision_status','accuracy','recent_accuracy','total_attempts','confidence','trend']],hide_index=True,use_container_width=True)
        st.subheader('Revision priority')
        for r in recs:
            prerequisite=f" Prerequisite to revisit: {r['prerequisite']}." if r.get('prerequisite') else ''
            st.write(f"**{r['topic']}** — {r['reason']}.{prerequisite} Suggested level: {r['suggested_difficulty']}.")
        st.subheader('Common errors by subtopic'); st.dataframe(mistake_summary(responses),hide_index=True,use_container_width=True)

elif page=='Study Plan':
    hero('A practical study plan','Your plan is generated from the latest mastery and practice history.')
    if st.button('Refresh plan') or not repo.tasks(student_id): repo.save_tasks(student_id,build_plan(recs))
    tasks=repo.tasks(student_id)
    if not tasks: st.info('Take a quiz to get a personalized study plan.')
    else:
        for t in tasks:
            checked=st.checkbox(f"Day {t['day_number']} · {t['topic']} — {t['task_text']}",value=bool(t['completed']),key=f"task_{t['task_id']}")
            if checked!=bool(t['completed']): repo.complete_task(t['task_id'],student_id,checked)
        st.caption('Refresh the plan after more quiz attempts to update priorities.')

elif page=='ML Insights':
    hero('How the prediction works','The model estimates question success from historical behavior and question difficulty.')
    if model is None:
        st.warning('No trained model found. In the project folder run: `python -m src.data.data_generator` then `python -m src.models.train`.')
    else:
        st.success(f"Selected model: **{model['model_name']}** · trained rows: {model['trained_rows']:,} · synthetic data")
        metrics=model['metrics']; st.dataframe(pd.DataFrame(metrics).T.rename_axis('Model').reset_index(),hide_index=True,use_container_width=True)
        selected_metrics=metrics[model['model_name']]
        st.subheader('Held-out, student-group evaluation'); st.write(f"ROC-AUC {selected_metrics['roc_auc']:.3f} · F1 {selected_metrics['f1']:.3f} · Precision {selected_metrics['precision']:.3f} · Recall {selected_metrics['recall']:.3f}")
        st.plotly_chart(px.imshow(selected_metrics['confusion_matrix'],text_auto=True,labels={'x':'Predicted','y':'Actual','color':'Count'},x=['Incorrect','Correct'],y=['Incorrect','Correct'],color_continuous_scale='Blues'),use_container_width=True)
        if model['model_name']=='Random Forest':
            importance=model['model'].feature_importances_; imp=pd.DataFrame({'Feature':model['feature_columns'],'Importance':importance}).sort_values('Importance',ascending=True); st.subheader('Feature importance'); st.plotly_chart(px.bar(imp,x='Importance',y='Feature',orientation='h',template='plotly_white'),use_container_width=True)
        else:
            coef=model['model'].named_steps['logisticregression'].coef_[0]; imp=pd.DataFrame({'Feature':model['feature_columns'],'Coefficient':coef}).sort_values('Coefficient'); st.subheader('Logistic regression coefficients'); st.plotly_chart(px.bar(imp,x='Coefficient',y='Feature',orientation='h',color='Coefficient',color_continuous_scale='RdBu',template='plotly_white'),use_container_width=True)
    st.info('Predictions are estimates, not judgments of intelligence or ability. Evaluation uses synthetic students and does not establish real-world validity.')
    if not responses.empty:
        bank=repo.question_rows(); last_topic=responses.iloc[-1]['topic']
        q=next((item for item in bank if item['topic']==last_topic),bank[0])
        future=pd.DataFrame([{'question_id':q['question_id'],'topic':q['topic'],'difficulty':q['difficulty'],'is_correct':0,'time_taken_seconds':q['estimated_time'],'attempt_number':1,'estimated_time':q['estimated_time'],'timestamp':pd.Timestamp.now()}])
        row=build_features(pd.concat([responses,future],ignore_index=True),include_target=False).iloc[-1].to_dict()
        pred=predict_probability(row,model)
        st.subheader('Example prediction from recorded history')
        if pred['probability'] is None: st.write(pred['reason'])
        else: st.write(f"Estimated probability of answering another **{q['difficulty'].lower()}** question in **{q['topic']}** correctly: **{pred['probability']:.0%}** ({pred['source']}).")

else:
    hero('About LearnLens AI','A local-first, explainable learning analytics portfolio project.')
    st.markdown('''LearnLens combines real supervised machine learning with transparent rule-based mastery and recommendation logic. Quiz results persist in a local SQLite database. **The ML training data is synthetic**, and model performance must not be presented as validated on real learners.

**How to explain it:** prior-only performance features feed a logistic regression and random forest. A student-group split evaluates generalization to held-out synthetic learners. The model with higher ROC-AUC is saved. Rules independently rank topics using mastery, recency, and sample confidence. Adaptive practice uses rules to adjust topic and difficulty.

Create a separate account for each learner. New accounts start with empty histories, and every dashboard, quiz, analytic, and study task is scoped to the signed-in account.''')

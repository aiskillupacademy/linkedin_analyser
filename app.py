import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
import numpy as np
from datetime import datetime,timedelta
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
llm  = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.2)

def linkedin_analyse(site):
    name = site.rstrip('/').split('/')[-1]
    headers = {
	#"X-RapidAPI-Key": "c3ed23db4emsh5054084058e4e2dp1a1780jsnaf404d8468f6",
    #"X-RapidAPI-Key": "dacc93bfecmsh336023176beccabp1fa929jsnbf31d1fec909",
    "X-RapidAPI-Key": "b3017e0b80mshd58e6b2078fd8edp1f1433jsnd946152af897",
	"X-RapidAPI-Host": "linkedin-data-api.p.rapidapi.com"    }
    profile_url = "https://linkedin-data-api.p.rapidapi.com/"
    posts_url = "https://linkedin-data-api.p.rapidapi.com/get-profile-posts"
    comments_url = "https://linkedin-data-api.p.rapidapi.com/get-profile-comments"
    r_posts = requests.get(posts_url, params= {"username":name}, headers=headers)
    r_profile = requests.get(profile_url, params ={"username":name}, headers=headers)
    r_comments = requests.get(comments_url, params ={"username":name}, headers=headers)
    print(r_posts.json())
    data_posts = pd.DataFrame(r_posts.json()['data'])
    data_profile = r_profile.json()
    data_comments = pd.DataFrame(r_comments.json()['data'])


    data_posts['postedDateTime'] = data_posts['postedDateTimestamp'].apply(lambda x: datetime.fromtimestamp(x/1000.0))
    last_30  = datetime.now() - timedelta(days=30)
    #print('{posts} posts made in last 30 days'.format(posts= len(data_posts.loc[data_posts['postedDateTime'] >= last_30])))
    try:
        num_posts= len(data_posts.loc[data_posts['postedDateTime'] >= last_30])
    except:
        num_posts =0
    #print('Last post made at {last_time}'.format(last_time = data_posts.loc[0]['postedDateTime'].strftime("%d/%m/%Y, %H:%M")))
    last_post = data_posts.loc[0]['postedDateTime'].strftime("%d/%m/%Y, %H:%M")
    data_comments['postedDaysAgo'] = data_comments['postedAt'].apply(lambda x: to_nodays(x))
    try:
        num_comments= len(data_comments.loc[data_comments['postedDaysAgo'] <= 30])
    except:
        num_comments =0
    last_comment = data_comments.loc[0]['postedAt']


    top_3 = data_posts.iloc[:3]
    lis_top3=[]
    for i,r in top_3.iterrows():
        lis_top3.append(r.to_dict())
    output = htmlfy(lis_top3, site).split('<h5>Regards<br>', 1)[0].split('<br>', 1)[1]

    html = "<h3>Profile analysis: </h3>"
    style = '''

    <style>
    .container {
        width: 100%;       margin: 0 auto;        padding: 0 15px;        box-sizing: border-box;

    }


    .row {
        margin: 0;        overflow: hidden;         border-style: solid;        border-color: gainsboro;        border-radius: 0px;
    }


    .col {
        float: left;        box-sizing: border-box;        padding: 10px;        height: 100%;        width: 33%;        overflow-wrap: break-word;
    }

    </style>

'''
    container = '''
    <div style="width: 100%;       margin: 0 auto;        padding: 0 15px;        box-sizing: border-box;">
    <div style="margin: 0;        overflow: hidden;         border-style: none;        border-color: gainsboro; ">
        <div style="float: left;        box-sizing: border-box;        padding: 10px;        height: 100%;        width: 33%;        overflow-wrap: break-word; text-align: center;">
            <img src="{image}" alt="" style="border-radius: 50%;" width=150; height=150> <br>
            <h5>{fname} {lname}</h5>
            <p>Lives in {location}</p>        
        </div>
        <div style="float: left;        box-sizing: border-box;        padding: 10px;        height: 100%;        width: 66%;        overflow-wrap: break-word;">
            <b>{headline}</b><br><br>
            <p><b>Education:</b> <br> {education}
                
            </p>
        </div>
    </div>
    <div style="margin: 0;        overflow: hidden;         border-style: none;        border-color: gainsboro;        border-radius: 0px;">
        <div style="float: left;        box-sizing: border-box;        padding: 10px;        height: 100%;        width: 50%;        overflow-wrap: break-word;">
            <h5>Languages</h5>
            {languages}
        </div>
    </div>
    <div style="margin: 0;        overflow: hidden;         border-style: none;        border-color: gainsboro;        border-radius: 0px;">
        <div style="float: left;        box-sizing: border-box;        padding: 10px;        height: 100%;        width: 33%;        overflow-wrap: break-word;">
            <h5>Engagement on Posts</h5>
            Median reactions: {med_react_count} <br>
            Median reposts: {med_repost_count} <br>
            Median comments: {med_comment_count}<br>
            
        </div>
        <div style="float: right;        box-sizing: border-box;        padding: 10px;        height: 100%;        width: 33%;        overflow-wrap: break-word;">
            <h5>Posts</h5>
            Self posts: {spost}  &emsp; Reposts: {rposts}<br>
            Posts in last 30 days: {num_posts}<br>
            Last posted: {last_post}
            <h5>Comments</h5>
            Median number of reactions: {med_comment_react_count} <br>
            Comments in last 30 days: {num_comments}<br>
            Last commented: {last_comment} ago
        </div>
    </div>
</div>

''' 
    print(data_profile['profilePicture'])
    html = html  + container
    languages = 'Not available'
    try:
        languages = '<br>'.join(['<b>'+i['name']+'</b> &emsp;Proficiency: '+i['proficiency'] for i in data_profile['languages']])
    except:
        pass
    headline = 'Headline Not Available'
    try:
        headline = data_profile['headline']
    except:
        pass
    education = 'Not available'
    try:
        education = '<br>'.join([i['degree']+' in '+i['fieldOfStudy'] for i in data_profile['educations']])
    except:
        pass
    location = 'Not Available'
    try:
        location = data_profile['geo']['full']
    except:
        pass
    try:
        med_react_count= data_posts['totalReactionCount'].median()
    except:
        med_react_count = 'unavailable'
    try:
        med_repost_count=data_posts['repostsCount'].median()
    except:
        med_repost_count = 'unavailable'
    try:
        med_comment_count=data_posts['commentsCount'].median()
    except:
        med_comment_count = 'unavailable'
    try:
        med_comment_react_count= data_comments['totalReactionCount'].median()
    except:
        med_comment_react_count = 'unavailable'
    try:
        spost = len(data_posts)- data_posts['reposted'].value_counts().to_dict()[True]
    except:
        spost = len(data_posts)
    try:
        rposts= data_posts['reposted'].value_counts().to_dict()[True]
    except:
        rposts = 0
    html = html.format(image = data_profile['profilePicture'], 
                       location= location, 
                       headline= headline, 
                       languages= languages,
                       #avg_post_len= round(data_posts['text'].apply(lambda x: len(x.split(' '))).sum()/len(data_posts['text']), 1), 
                       med_react_count= med_react_count,
                       med_repost_count=med_repost_count,
                       med_comment_count=med_comment_count,
                       #avg_comment_len= round(data_comments['text'].apply(lambda x: len(x.split(' '))).sum()/len(data_comments['text']), 1),
                       med_comment_react_count= med_comment_react_count,
                       education = education,
                       fname=data_profile['firstName'], lname=data_profile['lastName'],
                       spost = spost, rposts= rposts,
                       num_posts=num_posts, last_post=last_post, num_comments=num_comments, last_comment=last_comment
                       )
    
    try:
        endorsed_skills = pd.DataFrame(data_profile['skills'])
    except:
        endorsed_skills =pd.DataFrame()


    comments = data_comments['text'].to_list()
    messages_b5 = [{'role': 'system', 'content': '''
    Description:
    Welcome to the Big Five Personality Analyzer! This tool utilizes the renowned Big Five personality traits - Openness, Conscientiousness, Extraversion, Agreeableness, and Neuroticism - to analyze your personality based on your LinkedIn comments. By examining your language patterns and expressions, we'll provide you with insights into your personality traits, helping you better understand yourself and how you interact with others in a professional context.

    Instructions:
    Please provide a list of comments you've made on LinkedIn. These comments will serve as the basis for our analysis. The more comments you provide, the more accurate the analysis will be. Once you've input your comments, sit back and let the Big Five Personality Analyzer do its work! 
    Each score is out of 5.
    
    Example Input:
    1. Great article! I completely agree with your insights.
    2. Congratulations on your new role! Wishing you all the best.
    3. I appreciate the opportunity to connect with like-minded professionals.
    4. Interesting perspective. I hadn't considered that angle before.
    5. Thank you for sharing this valuable resource.

    Output:
    Openness:4.5
    Conscientiousness:3.8
    Extraversion:3.2
    Agreeableness:4.7
    Neuroticism:1.1
    '''}]
    for i in comments:
        messages_b5.append({'role': 'human', 'content': str(i)})
    messages_b5.append({'role': 'assistant', 'content': 'Based on your input, here are the scores for each of the Big Five personality traits. Higher scores indicate stronger alignment with that trait.  Separate each train by comma'})
    output_b5 = llm.invoke(messages_b5)
    #fig, ax = plt.subplots(figsize=(4, 2.5))
    #sns.set_theme(style='white', )
    b_5 = output_b5.content.replace('\n',',').split(',')
    b_5_df =[]
    print('b5',b_5)
    for i in b_5:
        try:
            trait, score = i.split(':')
        except:
            st.error("Error parsing linkedin profile, please try again!")
        b_5_df.append((trait, float(score)))
    b_5_df = pd.DataFrame(b_5_df, columns=['traits', 'scores'])
    #b_5_plot = sns.barplot(x='scores', y='traits',data=b_5_df, ax=ax,  palette='hls', width=0.5)
    #b_5_fig = plot_radar(b_5_df['traits'], b_5_df['scores'])
    
    messages_disc= [{'role': 'system', 'content': '''
    DISC Personality Analyzer
    Analyze personality traits based on the DISC model. DISC is a behavioral assessment tool. It categorizes personality into four main traits:
    Dominance - Their opinion is the final. direct, strong-willed, and forceful
    Influence - Open and place an emphasis on relationships and influencing or persuading others.
    Steadiness - tend to be dependable and place an emphasis on cooperation and sincerity. gentle and accommodating
    Conscientiousness -  tend to place an emphasis on quality, accuracy, expertise, and competency. analytical, and logical
    DiSC® is a personal assessment tool used to improve work productivity, teamwork, leadership, sales, and communication.
    Given a list of user comments, the assistant will analyze the language used and assign DISC scores for each category. The scoring criteria is:
    higher the user's comments resonate with a category, higher will be the score. 
    The following guardrails are maintained.
    - D and S scores cannot be similar as they are opposite traits.
    - I and C scores cannot be similar as they are opposite traits.
    - The scores are  range from 25 to 100
    Return output as a json object.
    Example:
    Input: User comments:
    1. "I will take charge and get things done!"
    2. "I enjoy socializing and networking with others."
    4. "Team work is more productive any day"
    Output: DISC scores
    {"Dominance (D)":70, "Influence(I)":50, "Steadiness(S)":50, "Conscientiousness(C)":20}
                     '''}]
    for i in comments:
        messages_disc.append({'role': 'human', 'content': str(i)})
    messages_disc.append({'role': 'assistant', 'content': 'Based on your input, scores for every DISC trait. Returning as a json file format.'})
    output_disc = llm.invoke(messages_disc)
    disc = json.loads(output_disc.content)

    
    

    posts_200c = data_posts['text'].to_list()
    posts_200c = [i[:300].replace(',', ' ').replace('\n', ' ') for i in posts_200c]
    message_schedule_class = [{'role':'system', 'content':'''
    You are an assistant which is given input a list of first 200 characters of 50 linkedin posts. From these posts derive 5 different bins, described by one word each into which these posts can be classified into. Each bin should be different from one another so that they can be used to classify the posts later. The bins should be logical. Bins should have,
    Examples of bin names: Industry, Technology, Engagement, Milestone, Trends, Opportunities, Networking, Leadership, Sustainability, Stakeholders etc
    The output should be a json object.
    Example: 
    Input >[
        "Exciting news! Our company just launched a new product.",
        "Looking for talented individuals to join our team.",
        "Here's a sneak peek of our upcoming webinar on digital marketing.",
        "Discussing the latest trends in artificial intelligence.",
        "Join us for a networking event next week.",
        "Congratulations to our team for winning the industry award!",
        "Launching a new initiative to support diversity and inclusion.",
        "Sharing insights from our recent market research.",
        # total 50 posts...]
Output json content>
'bins': ['Launches', 'Opportunities', 'Events', 'Industry', 'Insights']
'''}]
    for i in posts_200c:
        message_schedule_class.append({'role': 'human', 'content': str(i)})
    message_schedule_class.append({'role': 'assistant', 'content': 'Based on your input, here are the five bins for these posts.'})
    bins = json.loads(llm.invoke(message_schedule_class).content.replace('\n', ''))
    print('BINS', bins['bins'])
    message_schedule_classify = '''
    You are an assistant which is given input of first 200 characters of a linkedin post. You are also provided 5 different bins. Classify the post by assigning a bin which is most applicable to the post. Return  classifed post  as the bin name    

    Bins: {bins}   
    Post: {posts}
    Output format:<Bin of Post>'''
    chain  = RunnableLambda(lambda x: message_schedule_classify.format(bins=x['bins'], posts=x['posts'])) | llm
    class_list =[]
    for i in range(len(posts_200c)):
        p = chain.invoke({
            'bins':bins['bins'],
            'posts':posts_200c[i]
        }).content
        print('*', p)
        class_list.append(p)
    print('CLASSLIST', len(class_list))
    data_posts['dyn_class'] = class_list




    list_posts = ""
    for i in data_posts["text"]:
        list_posts = list_posts + i + "\n\n"
    prompt = """Given the set of linkedin posts by a user. 
    I want you to answer the following questions based on the above data. 

    1. Emotional language?
    2. Do they use clear, concise statements or lengthy sentences?
    3. Provide example and use cases vs just talk about the problem
    4. Does the post include personal greeting or acknowledgement to the customers?
    5. Do they present too many technical details?
    6. Do they provide any takeaways and action items
    7. Do they use high pressure or power words?
    8. Do they use facts or references?
    

    In the question, 'they' refer to the linkedin user.
    Don't give examples from posts. 

    posts: {posts}
    """
    chain_pi = RunnableLambda(lambda x: prompt.format(posts=x['posts'])) | llm | StrOutputParser()
    res = chain_pi.invoke({"posts": list_posts})
    ans_posts_insights = res.split("\n\n")

    list_comments = ""
    for i in data_comments["text"]:
        list_comments = list_comments + i + "\n\n"
    prompt = """Given the set of linkedin comments by a user. 
    I want you to answer the following questions based on the above data. 

    1. Emotional language?
    2. Do they use clear, concise statements or lengthy sentences?
    3. What is the tone of the comments?
    4. Do they use repetative language?   

    In the question, 'they' refer to the linkedin user.
    Don't give examples from posts. 

    posts: {comments}
    """
    chain_ci = RunnableLambda(lambda x: prompt.format(comments=x['comments'])) | llm | StrOutputParser()
    res = chain_ci.invoke({"comments": list_comments})
    ans_comments_insights = res.split("\n\n")
    

    return html, endorsed_skills, b_5_df, disc, data_posts, bins['bins'], ans_posts_insights, ans_comments_insights, output


def to_nodays(var):
        try:
            num = int(len(var)/2)
            val, scale = int(var[:num]), var[num:]
            if scale =='h':
                return 0
            elif scale == "d":
                return val
            elif scale == "w":
                return val*7
            elif scale == "mo":
                return val*30
            elif scale == "yr":
                return val*365
        except : 
            return None
        

def htmlfy(lis, site, mail='user@example.com', desc_as_summ=False):
        html = """
        <div style="font-family: Arial, Helvetica, sans-serif; font-size: medium;">
        <h5>Hi {email},</h5>
        Here are the latest LinkedIn posts by <a href='{site}'>{site}</a>.<br>
        """
        for i in lis:
            time = datetime.fromtimestamp(float(i['postedDateTimestamp'])/1000.0).strftime("%m/%d/%Y, %H:%M")
            is_reposted ='Self Posted'
            color='paleturquoise'
            if i['reposted'] == True:
                is_reposted = 'Reposted'
                color='moccasin'
            reactions = 0
            try:
                reactions = i['totalReactionCount']
            except:
                pass
            comments =0
            try:
                comments = i['commentsCount']
            except:
                pass
            reposts = 0
            try:
                reposts = i['repostsCount']
            except:
                pass
            container = '''
            <br>
            <div style='border-style: solid;    border-width: medium;    border-color: gainsboro;    border-radius: 10px;    padding: 10px; font-size: medium;'>
            <span><b>Posted at:</b> {time} &emsp;&emsp;</span> <span style='background-color: {color}; border-radius: 0px; padding: 5px;'>{is_reposted} </span> 
            <br>
            <span>{post}</span><br>
            <b>Post url:</b> <a href='{postUrl}'>{postUrl}</a>
            <div><span><b>Total reactions:</b> {reactions} &emsp;</span><span><b>Total comments:</b> {comments} &emsp;</span><span><b>Total reposts:</b> {reposts} &emsp;</span></div>
            '''
            image= None
            if i['image'] is not np.nan:
                container = container + '<img src="{image}"  style="display: block;     margin: auto;   width: 50%;     border-color: gainsboro;    border-radius: 0px;"> '
                image = i['image'][0]['url']
            html = html + container + '</div>'
            html = html.format(email=mail, site=site, post=i['text'], time=time, reactions=reactions, comments=comments, reposts=reposts, image=image, postUrl=i['postUrl'], is_reposted=is_reposted, color=color)
        html = html + '''<br>
        <h5>Regards<br>
        rava.ai</h5></div>'''
        return html
    

def plot_radar(labels, stats):
    angles=np.linspace(0, 2*np.pi, len(labels), endpoint=False)+0.31416
    fig, ax =plt.subplots( subplot_kw={'polar':True}, figsize=(2,2))
    ax.grid(color='thistle', linestyle='-', linewidth=0.5)
    ax.plot(angles , stats, '.-m', linewidth=0,)
    ax.set_title('Big 5', loc='left', fontdict={'fontsize':9})
    ax.fill(angles, stats, alpha=0.2, facecolor='deeppink', edgecolor='rebeccapurple', linewidth=2)
    ax.set_thetagrids(angles * 180/np.pi , labels, color='rebeccapurple', fontsize=8, )
    ax.set_rgrids(radii=(1,2,3,4,5), color='rebeccapurple', fontsize=8, alpha=0) 
    ax.set_rticks([1,2,3,4,5,6])
    ax.spines['polar'].set_visible(False)
    return fig



def posts_qa(data_posts):

    lst = ""
    for i in data_posts["text"]:
        lst = lst + i + "\n\n"


    prompt = """Given the set of linkedin posts by a user. 
    I want you to answer the following questions based on the above data. 

    1. Emotional language?
    2. Do they use clear, concise statements or lengthy sentences?
    3. Provide example and use cases vs just talk about the problem
    4. Does the post include personal greeting or acknowledgement to the customers?
    5. Do they present too many technical details?
    6. Do they provide any takeaways and action items
    7. Do they use high pressure or power words?
    8. Do they use facts or references?

    In the question, 'they' refer to the linkedin user.
    Don't give examples from posts. 

    posts: {posts}

    """
    chain = RunnableLambda(lambda x: prompt.format(posts=x['posts'])) | llm | StrOutputParser()
    res = chain.invoke({"posts": lst})
    ans = res.split("\n\n")
    return ans



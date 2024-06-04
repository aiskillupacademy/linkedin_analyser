from app import linkedin_analyse, plot_radar,posts_qa
import streamlit as st
import pandas as pd
from time import time
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
buff1, col, buff2 = st.columns([1,3,1])

col.title('Linkedin Apalyser App')
site = col.text_input("Enter website: ").rstrip('/')+'/'
col1,col2,col3, col4 = col.columns(4)

if col4.button('linkedin-analysis'):
    output, endorsed_skills, b_5_df, disc, data_posts, bins, q1, q2, output_posts = linkedin_analyse(site=site)
    container = col.container(border=True)
    
    container.html(output)
    skill_fig, skill_ax = plt.subplots(figsize=(20, 5))
    endorsed_skills.fillna(0)
    sns.set_theme(style='whitegrid')
    skill_plot = sns.barplot(data=endorsed_skills, x='name', y='endorsementsCount', width=0.5, color='#CCCCFF', legend=False)
    skill_plot.set_title('Skills', fontsize=12)
    skill_plot.set_xlabel('')
    skill_plot.tick_params(axis='x', rotation=90)
    container.pyplot(skill_fig, use_container_width=True)


    container.markdown('### Latest posts')
    container.html(output_posts)
    concol1, concol2 , concol3= st.columns([1,3,1])


    concol2.markdown('### LinkedIn routine')
    schedule_fig, ax2 = plt.subplots(figsize=(20, 5))
    weekday_hours = pd.DataFrame(columns=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
    for i in range(7):
        weekday_hours.loc[len(weekday_hours.index)] = [0]*24
    for wd, h in zip(data_posts['postedDateTime'].apply(lambda x: x.weekday()), data_posts['postedDateTime'].apply(lambda x: x.time().hour)):
        weekday_hours.loc[wd, h] += 1
    max_post_in_cell = weekday_hours.max().max()
    colormap=sns.light_palette("mediumblue", as_cmap=True)
    usage_plot = sns.heatmap(data=weekday_hours, 
                xticklabels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                yticklabels=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                square=True,ax=ax2,
                cmap= colormap,
                linewidths=2,
                linecolor='white',
                vmax=max_post_in_cell,
                vmin=0
                )
    usage_plot.set_title('LinkedIn Engagement\n', loc='right')
    usage_plot.set_xlabel(xlabel='Hours of the day', labelpad=10)
    concol2.pyplot(schedule_fig, use_container_width=True)
    
    with concol2.expander('More...'):
        for b in bins:
            schedule_fig, ax2 = plt.subplots(figsize=(20, 5))
            weekday_hours = pd.DataFrame(columns=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
            for i in range(7):
                weekday_hours.loc[len(weekday_hours.index)] = [0]*24
            for c, wd, h in zip(data_posts['dyn_class'],data_posts['postedDateTime'].apply(lambda x: x.weekday()), data_posts['postedDateTime'].apply(lambda x: x.time().hour)):
                if c == b:
                    weekday_hours.loc[wd, h] += 1
            colormap=sns.light_palette("mediumblue", as_cmap=True)
            usage_plot = sns.heatmap(data=weekday_hours, 
                        xticklabels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                        yticklabels=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                        square=True,ax=ax2,
                        cmap= colormap,
                        linewidths=2,
                        linecolor='white',
                        vmax=max_post_in_cell,
                        vmin=0
                        )
            usage_plot.set_title(b, loc='right')
            usage_plot.set_xlabel(xlabel='Hours of the day', labelpad=10)
            st.pyplot(schedule_fig, use_container_width=True)

    concol2.markdown('### Personality trait analysis')

    b_5_fig = plot_radar(["Openness", "Diligence", "Sociability", "Agreeability", "Anxiety"], b_5_df['scores'])
    concol2.pyplot(b_5_fig, use_container_width=False)

    disc_fig, disc_ax = plt.subplots(figsize=(6,2.5))
    disc_plot = sns.barplot(disc, color='#CCCCFF', width=0.5, ax=disc_ax, orient='h')
    disc_plot.set_title('DISC', fontsize=9)
    disc_plot.tick_params(axis='x', rotation=90)
    concol2.pyplot(disc_fig, use_container_width=True)
    
    post_analysis = posts_qa(data_posts=data_posts)
    concol2.markdown('### Posts analysis')
    for i in q1:
        concol2.write(i)
    concol2.markdown('### Comment analysis')
    for i in q2:
        concol2.write(i)



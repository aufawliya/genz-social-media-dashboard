import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Gen-Z Social Media Usage Dashboard",
    page_icon="📱",
    layout="wide"
)

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv('genz_social_media_usage_cleaned.csv')
    df['addiction_level'] = pd.Categorical(
        df['addiction_level'],
        categories=['Low', 'Medium', 'High'],
        ordered=True
    )
    return df

df = load_data()

# ============================================================
# DASHBOARD TITLE & DESCRIPTION
# ============================================================
st.title("📱 Gen-Z Social Media Usage Dashboard")
st.markdown("""
This dashboard explores social media usage patterns among Gen-Z users (aged 13–27),
focusing on platform popularity, daily usage time, and addiction level distribution.
""")

st.divider()

# ============================================================
# SIDEBAR FILTER (INTERACTIVITY)
# ============================================================
st.sidebar.header("🔍 Filters")

# Gender filter
all_genders = df['gender'].unique().tolist()
selected_genders = st.sidebar.multiselect(
    "Select Gender",
    options=all_genders,
    default=all_genders
)

# Age range filter
min_age, max_age = int(df['age'].min()), int(df['age'].max())
selected_age = st.sidebar.slider(
    "Select Age Range",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age)
)

# Apply filters
filtered_df = df[
    (df['gender'].isin(selected_genders)) &
    (df['age'] >= selected_age[0]) &
    (df['age'] <= selected_age[1])
]

# Show how many records are currently shown
st.sidebar.markdown(f"**Records shown:** {len(filtered_df):,}")

st.divider()

# ============================================================
# OBJECTIVE 1: PLATFORM POPULARITY
# ============================================================
st.subheader("📊 Objective 1: Most Commonly Used Social Media Platforms")

platform_counts = filtered_df.groupby('primary_platform').agg(
    user_count=('primary_platform', 'count')
).reset_index().sort_values('user_count', ascending=False)

fig1, ax1 = plt.subplots(figsize=(8, 4))
ax1.bar(
    platform_counts['primary_platform'],
    platform_counts['user_count'],
    color=['#E1306C', '#1DA1F2', '#FF0050', '#FF0000', '#FFFC00'],
    edgecolor='white'
)
ax1.set_title('Number of Gen-Z Users by Primary Social Media Platform', fontsize=14, fontweight='bold')
ax1.set_xlabel('Social Media Platform', fontsize=12)
ax1.set_ylabel('Number of Users', fontsize=12)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

for bar, val in zip(ax1.patches, platform_counts['user_count']):
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1000,
        f'{int(val):,}',
        ha='center', va='bottom', fontsize=10
    )

plt.tight_layout()
st.pyplot(fig1)
plt.close()

st.divider()

# ============================================================
# OBJECTIVE 2: AVERAGE DAILY USAGE BY PLATFORM
# ============================================================
st.subheader("⏱️ Objective 2: Average Daily Usage Time by Platform")

avg_usage = filtered_df.groupby('primary_platform').agg(
    avg_daily_hours=('daily_usage_hours', 'mean')
).reset_index()

avg_usage['avg_daily_hours'] = avg_usage['avg_daily_hours'].round(2)

fig2, ax2 = plt.subplots(figsize=(7, 7))

ax2.pie(
    avg_usage['avg_daily_hours'],
    labels=avg_usage['primary_platform'],
    autopct='%1.1f%%',
    startangle=90
)

ax2.set_title(
    'Share of Average Daily Social Media Usage Hours by Platform',
    fontsize=14,
    fontweight='bold'
)

plt.tight_layout()
st.pyplot(fig2)
plt.close()

# ============================================================
# OBJECTIVE 3: ADDICTION LEVEL DISTRIBUTION BY PLATFORM
# ============================================================
st.subheader("⚠️ Objective 3: Addiction Level Distribution by Platform")

addiction_dist = filtered_df.groupby(
    ['primary_platform', 'addiction_level'], observed=True
).agg(
    user_count=('addiction_level', 'count')
).reset_index()

platforms = addiction_dist['primary_platform'].unique()
addiction_levels = ['Low', 'Medium', 'High']
colors = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'}

x = range(len(platforms))
width = 0.25

fig3, ax3 = plt.subplots(figsize=(10, 5))

for i, level in enumerate(addiction_levels):
    level_data = addiction_dist[addiction_dist['addiction_level'] == level].copy()
    level_data['addiction_level'] = level_data['addiction_level'].astype(str)  # ← fix: drop categorical type
    level_data = level_data.set_index('primary_platform').reindex(platforms, fill_value=0)
    ax3.bar(
        [pos + i * width for pos in x],
        level_data['user_count'],
        width=width,
        label=level,
        color=colors[level],
        edgecolor='white'
    )

ax3.set_title('Addiction Level Distribution Across Social Media Platforms', fontsize=14, fontweight='bold')
ax3.set_xlabel('Social Media Platform', fontsize=12)
ax3.set_ylabel('Number of Users', fontsize=12)
ax3.set_xticks([pos + width for pos in x])
ax3.set_xticklabels(platforms)
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
ax3.legend(title='Addiction Level', fontsize=10)

plt.tight_layout()
st.pyplot(fig3)
plt.close()

st.divider()

# ============================================================
# FOOTER
# ============================================================
st.caption("Data Source: Gen-Z Social Media Usage Dataset (Kaggle) | Dashboard built with Streamlit")

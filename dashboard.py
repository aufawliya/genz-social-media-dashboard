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

platform_colors = ['#FFB3C1', '#FFDDA1', '#B5EAD7', '#C7CEEA', '#FFFACD']
addiction_colors = {'Low': '#B5EAD7', 'Medium': '#FFDDA1', 'High': '#FFB3C1'}
font = 'Palatino Linotype'

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

all_genders = df['gender'].unique().tolist()
selected_genders = st.sidebar.multiselect(
    "Select Gender",
    options=all_genders,
    default=all_genders
)

min_age, max_age = int(df['age'].min()), int(df['age'].max())
selected_age = st.sidebar.slider(
    "Select Age Range",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age)
)

filtered_df = df[
    (df['gender'].isin(selected_genders)) &
    (df['age'] >= selected_age[0]) &
    (df['age'] <= selected_age[1])
]

st.sidebar.markdown(f"**Records shown:** {len(filtered_df):,}")

st.divider()

# ============================================================
# OBJECTIVE 1: PLATFORM POPULARITY — PIE CHART
# ============================================================
st.subheader("📊 Objective 1: Most Commonly Used Social Media Platforms")

platform_counts = filtered_df.groupby('primary_platform').agg(
    user_count=('primary_platform', 'count')
).reset_index().sort_values('user_count', ascending=False)

fig1, ax1 = plt.subplots(figsize=(7, 7))
ax1.pie(
    platform_counts['user_count'],
    labels=platform_counts['primary_platform'],
    autopct='%1.1f%%',
    colors=platform_colors,
    startangle=140,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
    textprops={'fontfamily': font, 'fontsize': 11}
)
ax1.set_title(
    'Distribution of Gen-Z Users by Primary Social Media Platform',
    fontsize=14, fontweight='bold', fontfamily=font
)
ax1.axis('equal')

plt.tight_layout()
st.pyplot(fig1)
plt.close()

st.divider()

# ============================================================
# OBJECTIVE 2: AVERAGE DAILY USAGE — LINE PLOT
# ============================================================
st.subheader("📈 Objective 3: Average Daily Usage Hours by Platform")

# Bold colour palette
platform_colors = ['#FF1493',  # Deep Pink
                   '#FF4500',  # Orange Red
                   '#32CD32',  # Lime Green
                   '#1E90FF',  # Dodger Blue
                   '#FFD700']  # Gold

font = 'Palatino Linotype'

# Grouping
avg_usage = df.groupby('primary_platform')['daily_usage_hours'].mean()

# Create figure and axis
fig2, ax2 = plt.subplots(figsize=(8, 5))

# Background
fig2.patch.set_facecolor('#FFF0F5')
ax2.set_facecolor('#FFF0F5')

# Hot pink dotted line
avg_usage.plot(kind='line', marker='o', ax=ax2,
               color='hotpink', linestyle='--', linewidth=2,
               markeredgecolor='white', markeredgewidth=1.5, markersize=8)

# Bold colours for each point
for i, (x_val, y_val, color) in enumerate(zip(avg_usage.index, avg_usage.values, platform_colors)):
    ax2.plot(x_val, y_val, marker='o', markersize=10,
             color=color, markeredgecolor='white', markeredgewidth=1.5)

# Titles and labels
ax2.set_title('Average Daily Usage Time by Platform',
              fontsize=14, fontweight='bold', fontfamily=font)
ax2.set_xlabel('Platform', fontsize=12, fontfamily=font)
ax2.set_ylabel('Average Daily Usage Hours', fontsize=12, fontfamily=font)

# Apply font to tick labels
for tick in ax2.get_xticklabels() + ax2.get_yticklabels():
    tick.set_fontfamily(font)

plt.tight_layout()
st.pyplot(fig2)
plt.close()

st.divider()

# ============================================================
# OBJECTIVE 3: ADDICTION LEVEL DISTRIBUTION — GROUPED BAR
# ============================================================
st.subheader("⚠️ Objective 3: Addiction Level Distribution by Platform")

addiction_dist = filtered_df.groupby(
    ['primary_platform', 'addiction_level'], observed=True
).agg(
    user_count=('addiction_level', 'count')
).reset_index()

platforms = addiction_dist['primary_platform'].unique()
addiction_levels = ['Low', 'Medium', 'High']
x = range(len(platforms))
width = 0.25

fig3, ax3 = plt.subplots(figsize=(10, 5))

for i, level in enumerate(addiction_levels):
    level_data = addiction_dist[addiction_dist['addiction_level'] == level].copy()
    level_data['addiction_level'] = level_data['addiction_level'].astype(str)
    level_data = level_data.set_index('primary_platform').reindex(platforms, fill_value=0)
    ax3.bar(
        [pos + i * width for pos in x],
        level_data['user_count'],
        width=width,
        label=level,
        color=addiction_colors[level],  # ← fixed: was addiction_colors (wrong)
        edgecolor='white'
    )

ax3.set_title('Addiction Level Distribution Across Social Media Platforms',
              fontsize=14, fontweight='bold', fontfamily=font)
ax3.set_xlabel('Social Media Platform', fontsize=12, fontfamily=font)
ax3.set_ylabel('Number of Users', fontsize=12, fontfamily=font)
ax3.set_xticks([pos + width for pos in x])
ax3.set_xticklabels(platforms, fontfamily=font)
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

for tick in ax3.get_yticklabels():
    tick.set_fontfamily(font)

ax3.legend(title='Addiction Level', fontsize=10, title_fontsize=10,
           prop={'family': font})

plt.tight_layout()
st.pyplot(fig3)
plt.close()

st.divider()

# ============================================================
# FOOTER
# ============================================================
st.caption("Data Source: Gen-Z Social Media Usage Dataset (Kaggle) | Dashboard built with Streamlit")

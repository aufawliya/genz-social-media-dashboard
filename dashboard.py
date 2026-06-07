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

def set_chart_background(fig, ax, color="#FFF0F5"):
    fig.patch.set_facecolor('#FFD6E0')  # outer pink
    ax.set_facecolor(color)             # inner lighter pink

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
# SIDEBAR FILTERS
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
# SUMMARY STATS — METRIC CARDS
# ============================================================
st.subheader("📈 Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 Total Users",
        value=f"{len(filtered_df):,}"
    )

with col2:
    avg_age = round(filtered_df['age'].mean(), 1)
    st.metric(
        label="🎂 Average Age",
        value=f"{avg_age} yrs"
    )

with col3:
    avg_hours = round(filtered_df['daily_usage_hours'].mean(), 2)
    st.metric(
        label="⏱️ Avg Daily Usage",
        value=f"{avg_hours} hrs"
    )

with col4:
    top_platform = filtered_df['primary_platform'].value_counts().idxmax()
    st.metric(
        label="🏆 Top Platform",
        value=top_platform
    )

st.divider()

# ============================================================
# ROW 1 — OBJECTIVE 1 (left) + OBJECTIVE 2 (right)
# ============================================================
col_left, col_right = st.columns(2)

# --- OBJECTIVE 1: PIE CHART ---
with col_left:
    st.subheader("📊 Objective 1: Most Commonly Used Social Media Platforms")

    platform_counts = filtered_df.groupby('primary_platform').agg(
        user_count=('primary_platform', 'count')
    ).reset_index().sort_values('user_count', ascending=False)

    fig1, ax1 = plt.subplots(figsize=(6, 6))
    set_chart_background(fig1, ax1)
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
        fontsize=13, fontweight='bold', fontfamily=font
    )
    ax1.axis('equal')
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close()

# --- OBJECTIVE 2: MEAN PLOT ---
with col_right:
    st.subheader("📈 Objective 2: Average Daily Usage Hours by Platform")

    avg_usage = filtered_df.groupby('primary_platform').agg(
        avg_daily_hours=('daily_usage_hours', 'mean')
    ).reset_index().sort_values('avg_daily_hours', ascending=False)
    avg_usage['avg_daily_hours'] = avg_usage['avg_daily_hours'].round(2)

    fig2, ax2 = plt.subplots(figsize=(6, 6))
    set_chart_background(fig2, ax2)

    ax2.plot(
        avg_usage['primary_platform'],
        avg_usage['avg_daily_hours'],
        marker='o',
        linewidth=2,
        linestyle='--',
        color='#FFB3C1',
        markersize=10,
        markeredgecolor='white',
        markeredgewidth=1.5
    )

    for x_val, y_val, color in zip(
        avg_usage['primary_platform'],
        avg_usage['avg_daily_hours'],
        platform_colors
    ):
        ax2.plot(x_val, y_val, marker='o', markersize=12,
                 color=color, markeredgecolor='white', markeredgewidth=1.5)
        ax2.text(x_val, y_val + 0.02, f'{y_val:.2f} hrs',
                 ha='center', va='bottom', fontsize=10, fontfamily=font)

    ax2.set_title('Average Daily Usage Hours by Platform',
                  fontsize=13, fontweight='bold', fontfamily=font)
    ax2.set_xlabel('Social Media Platform', fontsize=11, fontfamily=font)
    ax2.set_ylabel('Average Daily Usage (Hours)', fontsize=11, fontfamily=font)
    ax2.set_ylim(
    avg_usage['avg_daily_hours'].min() - 0.05,
    avg_usage['avg_daily_hours'].max() + 0.05
)

    for tick in ax2.get_xticklabels() + ax2.get_yticklabels():
        tick.set_fontfamily(font)

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

st.divider()

# ============================================================
# ROW 2 — OBJECTIVE 3 (full width)
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
set_chart_background(fig3, ax3)

for i, level in enumerate(addiction_levels):
    level_data = addiction_dist[addiction_dist['addiction_level'] == level].copy()
    level_data['addiction_level'] = level_data['addiction_level'].astype(str)
    level_data = level_data.set_index('primary_platform').reindex(platforms, fill_value=0)
    ax3.bar(
        [pos + i * width for pos in x],
        level_data['user_count'],
        width=width,
        label=level,
        color=addiction_colors[level],
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

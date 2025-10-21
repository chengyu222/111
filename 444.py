import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="个人信息管理系统", page_icon="🌱", layout="wide")

BASE_DIR = Path().parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "records.csv"
DATA_DIR.mkdir(parents=True, exist_ok=True)

st.title("个人信息管理系统")
st.caption("轻松管理你的竞赛获奖、学习经历、工作记录等信息")

COLUMNS = ["id", "title", "category", "level", "organization", "notes", "created_at"]

def load_data() -> pd.DataFrame:
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame(columns=COLUMNS)
    return df

def save_data(df: pd.DataFrame):
    try:
        df.to_csv(CSV_PATH, index=False)
        pass
    except Exception:
        # 回退，忽略保存错误，保证应用不中断
        pass

def input_form(df: pd.DataFrame) -> pd.DataFrame:
    st.subheader("添加新记录")

    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            new = {}
            new["title"] = st.text_input("标题", placeholder="例如：全国大学生数学建模竞赛")
            CATEGORIES = ["荣誉", "竞赛", "证书", "教育经历", "实践经历", "项目经历", "其他"]
            new["category"] = st.selectbox("类别", CATEGORIES, index=0)

        with col2:
            LEVELS = ["", "国家级", "省级", "市级", "校级", "院级"]
            new["level"] = st.selectbox("级别", LEVELS, index=0)
            new["organization"] = st.text_input("颁发机构", placeholder="例如：教育部")

        new["notes"] = st.text_area("备注", placeholder="详细描述、成果、技能等", height=100)

        submitted = st.form_submit_button("保存记录", type="primary", use_container_width=True)

        if submitted:
            if not new["title"]:
                st.error("请填写标题！")
                return df

            new["id"] = 1 if df.empty else int(df["id"].max()) + 1
            new["created_at"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            df_new = pd.DataFrame([new])
            df = pd.concat([df, df_new], ignore_index=True)
            save_data(df)
            st.success("✅ 记录已保存！")

    return df

def filter_data(df):
    st.sidebar.subheader("筛选条件")

    categories = ["全部"] + list(df["category"].unique())
    selected_category = st.sidebar.selectbox("按类别筛选", categories)

    levels = ["全部"] + [l for l in df["level"].unique() if l]
    selected_level = st.sidebar.selectbox("按级别筛选", levels)

    filtered_df = df.copy()

    if selected_category != "全部":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]

    if selected_level != "全部":
        filtered_df = filtered_df[filtered_df["level"] == selected_level]

    return filtered_df

def format_output(df, format_type="markdown"):
    """按指定格式输出数据"""
    if format_type == "markdown":
        output = "个人经历记录\n\n"
        for _, row in df.iterrows():
            output += f" {row['title']}\n"
            output += f"类别: {row['category']}\n"
            if row['level']:
                output += f"级别: {row['level']}\n"
            if row['organization']:
                output += f"机构: {row['organization']}\n"
            if row['notes']:
                output += f"备注: {row['notes']}\n"
            output += "\n"
        return output

    elif format_type == "simple":
        output = ""
        for _, row in df.iterrows():
            output += f"{row['title']}"
            if row['level']:
                output += f" ({row['level']})"
            output += "\n"
        return output

    elif format_type == "csv":
        return df.to_csv(index=False)

df = load_data()
df = input_form(df)
st.divider()

if not df.empty:
    st.subheader("所有记录")

    filtered_df = filter_data(df)

    st.info(f"显示 {len(filtered_df)} 条记录（共 {len(df)} 条）")

    st.dataframe(
        filtered_df[["title", "category", "level", "organization"]],
        use_container_width=True,
        hide_index=True
    )

    with st.expander("查看详细信息"):
        for _, row in filtered_df.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{row['title']}")
                    st.caption(f"类别: {row['category']} | 级别: {row['level']}")
                    if row['organization']:
                        st.caption(f"机构: {row['organization']}")
                    if row['notes']:
                        st.write(row['notes'])
                with col2:
                    if st.button("delete", key=f"del_{row['id']}"):
                        df = df[df["id"] != row["id"]]
                        save_data(df)
                        st.rerun()
                st.divider()

    st.subheader("导出数据")

    col1, col2 = st.columns(2)

    with col1:
        format_type = st.selectbox("输出格式", ["markdown", "simple", "csv"])
        output_text = format_output(filtered_df, format_type)
        st.text_area("格式化输出", output_text, height=200)

    with col2:
        st.download_button(
            label="下载CSV文件",
            data=filtered_df.to_csv(index=False),
            file_name="personal_records.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.write("数据统计")
        st.metric("总记录数", len(df))
        st.metric("筛选记录数", len(filtered_df))
        category_counts = df["category"].value_counts()
        st.write("类别分布:")
        for category, count in category_counts.items():
            st.write(f"- {category}: {count}")

else:
    st.info("💡 还没有任何记录，请在上方添加你的第一条记录！")
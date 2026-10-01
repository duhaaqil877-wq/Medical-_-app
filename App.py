import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
from datetime import datetime

# -------------------------------------------------------------------
# 1. إعدادات الصفحة
# -------------------------------------------------------------------
st.set_page_config(
    page_title="نظام دعم القرار الطبي",
    page_icon="🩺",
    layout="wide"
)
hide_footer_style = """
    <style>
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)
    <style>
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)
# -------------------------------------------------------------------
# 2. قاعدة بيانات التحاليل الشاملة مع المعدلات الطبيعية
# -------------------------------------------------------------------
TEST_LABELS = {
    "WBC": "خلايا الدم البيضاء (WBC)",
    "RBC": "خلايا الدم الحمراء (RBC)",
    "Hb": "الهيموجلوبين (Hb)",
    "PLT": "الصفائح الدموية (PLT)",
    "FBS": "سكر الدم الصائم (FBS)",
    "HbA1c": "السكر التراكمي (HbA1c)",
    "Urea": "اليوريا (Urea)",
    "Creatinine": "الكرياتينين (Creatinine)",
    "ALT": "إنزيم الكبد (ALT)",
    "AST": "إنزيم الكبد (AST)",
    "TSH": "الهرمون المنبه للدرقية (TSH)",
    "Cholesterol": "الكوليسترول الكلي (Cholesterol)"
}

RANGES = {
    "WBC": (4.0, 11.0, "x10^3/µL"),
    "RBC": (4.2, 5.9, "x10^6/µL"),
    "Hb": (12.0, 17.5, "g/dL"),
    "PLT": (150, 450, "x10^3/µL"),
    "FBS": (70, 99, "mg/dL"),
    "HbA1c": (4.0, 5.6, "%"),
    "Urea": (15, 45, "mg/dL"),
    "Creatinine": (0.6, 1.2, "mg/dL"),
    "ALT": (7, 56, "U/L"),
    "AST": (10, 40, "U/L"),
    "TSH": (0.4, 4.0, "mIU/L"),
    "Cholesterol": (125, 200, "mg/dL")
}

# -------------------------------------------------------------------
# 3. الدوال المساعدة (تحليل وقراءة النتائج)
# -------------------------------------------------------------------
def analyze_lab_results(data):
    abnormalities = []
    normal_count = 0
    total = len(data)
    
    for test, val in data.items():
        low, high, unit = RANGES[test]
        if val < low:
            abnormalities.append(f"• **{TEST_LABELS[test]}**: منخفض ({val} {unit}) - المعدل الطبيعي: {low}-{high}")
        elif val > high:
            abnormalities.append(f"• **{TEST_LABELS[test]}**: مرتفع ({val} {unit}) - المعدل الطبيعي: {low}-{high}")
        else:
            normal_count += 1
            
    return abnormalities, normal_count, total

def generate_pdf(patient_name, patient_age, patient_gender, data, summary):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # العنوان
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=12
    )
    story.append(Paragraph("Medical Decision Support Report", title_style))
    story.append(Spacer(1, 12))

    # معلومات المريض
    p_info = f"<b>Patient Name:</b> {patient_name} | <b>Age:</b> {patient_age} | <b>Gender:</b> {patient_gender}<br/>"
    p_info += f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    story.append(Paragraph(p_info, styles['Normal']))
    story.append(Spacer(1, 18))

    # النتائج
    story.append(Paragraph("<b>Laboratory Test Results:</b>", styles['Heading2']))
    for test, val in data.items():
        low, high, unit = RANGES[test]
        status = "Normal"
        if val < low:
            status = "LOW"
        elif val > high:
            status = "HIGH"
        line = f"{TEST_LABELS[test]}: {val} {unit} [{status}] (Ref: {low}-{high})"
        story.append(Paragraph(line, styles['Normal']))

    story.append(Spacer(1, 18))
    story.append(Paragraph("<b>Clinical Recommendation:</b>", styles['Heading2']))
    story.append(Paragraph(summary, styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------------------------------------------
# 4. الواجهة الرئيسية والتطبيق
# -------------------------------------------------------------------
st.title("🩺 نظام دعم القرار الطبي التشخيصي (CDSS)")
st.write("أدخل بيانات المريض ونتائج التحاليل للحصول على تقييم وتوصيات أولية.")

st.markdown("---")

# معلومات المريض
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    patient_name = st.text_input("اسم المريض", "أحمد محمود")
with col_p2:
    patient_age = st.number_input("العمر", min_value=1, max_value=120, value=35)
with col_p3:
    patient_gender = st.selectbox("الجنس", ["ذكر", "أنثى"])

st.markdown("---")
st.subheader("📋 نتائج التحاليل المخبرية")

# إدخال نتائج التحاليل عبر أعمدة متناسقة
user_inputs = {}
cols = st.columns(3)

for idx, (test, label) in enumerate(TEST_LABELS.items()):
    low, high, unit = RANGES[test]
    with cols[idx % 3]:
        default_val = float((low + high) / 2)
        user_inputs[test] = st.number_input(
            f"{label} ({unit})",
            min_value=0.0,
            max_value=10000.0,
            value=round(default_val, 1),
            step=0.1
        )

st.markdown("---")

# زر التحليل وتقييم الحالة
if st.button("🔍 تحليل النتائج وإصدار التوصية", type="primary"):
    abnormalities, normal_count, total = analyze_lab_results(user_inputs)
    
    st.subheader("📊 ملخص التقييم الطبي")
    st.info(f"عدد التحاليل السليمة: **{normal_count}** من أصل **{total}**")
    
    if abnormalities:
        st.warning("⚠️ **القراءات غير الطبيعية المسجلة:**")
        for ab in abnormalities:
            st.markdown(ab)
            
        recommendation = "توجد بعض القراءات الخارجة عن المعدل الطبيعي. يُنصح بمراجعة الطبيب المختص لتقييم الأعراض السريرية وإجراء الفحوصات التكميلية اللازمة."
    else:
        st.success("✅ **جميع القراءات ضمن المعدلات الطبيعية.**")
        recommendation = "التحاليل سليمة بشكل عام. ينصح بالحفاظ على نمط حياة صحي والمتابعة الدورية."

    st.markdown("---")
    st.subheader("📄 التوصية السريرية")
    st.write(recommendation)

    # إنشاء وتنزيل تقرير PDF
    pdf_buffer = generate_pdf(patient_name, patient_age, patient_gender, user_inputs, recommendation)
    st.download_button(
        label="📥 تحميل التقرير الطبي (PDF)",
        data=pdf_buffer,
        file_name=f"Medical_Report_{patient_name}.pdf",
        mime="application/pdf"
    )

import streamlit as st
from food_database import food_database

# إعدادات الصفحة لتظهر بشكل رائع على الموبايل
st.set_page_config(page_title="مساعد مريض السكري الذكي", page_icon="🩺", layout="centered")

st.title("🩺 مساعد مريض السكري الذكي")
st.write("أدخل بياناتك الشخصية ومستوى نشاطك لحساب احتياجاتك من السعرات والكربوهيدرات.")

# خانات الإدخال (تظهر بشكل جميل في المتصفح)
with st.sidebar:
    st.header("بياناتك الشخصية")
    name = st.text_input("الاسم:", "")
    age = st.number_input("العمر بالسنوات:", min_value=1, max_value=120, value=30)
    sex = st.selectbox("النوع:", ["ذكر", "أنثى"])
    weight = st.number_input("الوزن بالكيلو:", min_value=1.0, max_value=300.0, value=70.0, step=0.1)
    height = st.number_input("الطول بالسنتيمتر:", min_value=50.0, max_value=250.0, value=170.0, step=0.1)
    activity_level_str = st.selectbox(
        "مستوى النشاط:",
        ["1: خامل (قليل الحركة)", "2: نشاط خفيف (رياضة 1-3 أيام/أسبوع)", "3: نشاط متوسط (رياضة 3-5 أيام/أسبوع)", "4: نشاط عالي (رياضة يومية)"]
    )

# استخراج رقم مستوى النشاط من النص
activity = int(activity_level_str.split(":")[0])

# 3. حساب الـ BMR الأساسي (الفصل 6: المنطق الشرطي)
if sex == "ذكر":
    bmr_base = (10 * weight) + (6.25 * height) - (5 * age) + 5
else:
    bmr_base = (10 * weight) + (6.25 * height) - (5 * age) - 161

# 4. حساب إجمالي السعرات بناءً على النشاط (الفصل 6: الجمل الشرطية المتعددة elif)
activity_status = ""
if activity == 1:
    total_calories = bmr_base * 1.2
    activity_status = "جسمك خامل! تحتاج لنشاط كثير"
elif activity == 2:
    total_calories = bmr_base * 1.375
    activity_status = "جسمك غير نشط! تحتاج لنشاط أكثر"
elif activity == 3:
    total_calories = bmr_base * 1.55
    activity_status = "نشاط متوسط! ابذل المزيد"
else:
    total_calories = bmr_base * 1.725
    activity_status = "نشاط عالي! استمر"

# 5. حساب الكربوهيدرات لمرضى السكري (المنطق الحسابي - الفصل 5)
carbo_needed = (total_calories * 0.45) / 4
carbo_per_meal = carbo_needed / 3

st.divider()

st.subheader("📊 ملخص احتياجاتك اليومية")
st.write(f"مرحباً يا **{name}**")
st.info(activity_status)
st.metric("احتياج جسمك الأساسي (BMR)", f"{round(bmr_base)} سعر حراري")
st.metric("إجمالي السعرات التي تحتاجها يومياً", f"{round(total_calories)} سعر حراري")
st.metric("احتياجك اليومي الكلي من الكربوهيدرات", f"{round(carbo_needed)} جرام")
st.metric("المسموح لك في الوجبة الواحدة", f"{round(carbo_per_meal)} جرام")

st.divider()

st.subheader("🍽️ تحليل وجبتك الحالية")

# قائمة الطعام من القاموس
food_items = list(food_database.keys())
selected_food = st.selectbox("اختر نوع الطعام الذي تناولته:", food_items)
quantity_grams = st.number_input(f"أدخل الكمية بالجرام لـ {selected_food}:", min_value=0.0, value=100.0, step=1.0)

carbo_eaten = 0.0
calories_eaten = 0.0
if selected_food:
    food_info = food_database[selected_food]
    # نحسب الكربوهيدرات والسعرات بناءً على الكمية المدخلة
    carbo_eaten = (food_info["carbs"] / 100) * quantity_grams
    calories_eaten = (food_info["calories"] / 100) * quantity_grams

st.write(f"كمية الكربوهيدرات في {round(quantity_grams)} جرام من {selected_food}: **{round(carbo_eaten, 2)} جرام**")
st.write(f"كمية السعرات الحرارية في {round(quantity_grams)} جرام من {selected_food}: **{round(calories_eaten, 2)} سعر حراري**")

if carbo_eaten > 0:
    if carbo_eaten > carbo_per_meal + 5:
        st.warning(f"⚠️ تنبيه: هذه الوجبة تحتوي على كربوهيدرات زائدة عن المسموح لك! الزيادة هي: {round(carbo_eaten - carbo_per_meal)} جرام")
    elif carbo_eaten < carbo_per_meal - 5:
        st.info(f"ℹ️ ملحوظة: وجبتك تحتوي على كربوهيدرات أقل من احتياجك. النقص هو: {round(carbo_per_meal - carbo_eaten)} جرام")
    else:
        st.success("✅ أحسنت! وجبتك متوازنة وضمن نطاق الأمان الصحي.")
else:
    st.write("اختر طعاماً وأدخل الكمية لتحليلها.")

st.divider()

st.subheader("💡 اقتراحات وجبات صحية")

# حساب السعرات والكربوهيدرات المتبقية لليوم (افتراضياً لم يتم تناول أي وجبات أخرى)
# هذا الجزء يمكن تطويره لاحقاً لتتبع الوجبات على مدار اليوم
remaining_calories = total_calories - calories_eaten
remaining_carbs = carbo_needed - carbo_eaten

st.write(f"متبقي لك اليوم حوالي **{round(remaining_calories)} سعر حراري** و **{round(remaining_carbs)} جرام كربوهيدرات**.")

suggestions = []

# اقتراحات لوجبة رئيسية (إذا كان المتبقي كبير)
if remaining_calories > 400 and remaining_carbs > 30:
    suggestions.append("وجبة رئيسية:")
    for food, info in food_database.items():
        if info["calories"] <= remaining_calories * 0.5 and info["carbs"] <= remaining_carbs * 0.5 and info["calories"] > 100:
            suggestions.append(f"- {food} (حوالي {round(info['calories'])} سعر و {round(info['carbs'])} جرام كربوهيدرات لكل 100 جرام)")
    if len(suggestions) == 1: # No main meal suggestions found
        suggestions.append("لا توجد اقتراحات لوجبة رئيسية ضمن الميزانية المتبقية.")

# اقتراحات لسناك (إذا كان المتبقي متوسط)
if remaining_calories > 100 and remaining_carbs > 10:
    if len(suggestions) > 0: # Add a separator if main meal suggestions exist
        suggestions.append("\nسناك صحي:")
    else:
        suggestions.append("سناك صحي:")
    for food, info in food_database.items():
        if info["calories"] <= remaining_calories * 0.3 and info["carbs"] <= remaining_carbs * 0.3 and info["calories"] > 20:
            suggestions.append(f"- {food} (حوالي {round(info['calories'])} سعر و {round(info['carbs'])} جرام كربوهيدرات لكل 100 جرام)")
    if len(suggestions) == 1 or (len(suggestions) > 1 and suggestions[-1] == "\nسناك صحي:"): # No snack suggestions found
        suggestions.append("لا توجد اقتراحات لسناك ضمن الميزانية المتبقية.")

if not suggestions:
    st.write("لا توجد اقتراحات حالياً. قد تكون قد استهلكت معظم احتياجاتك اليومية.")
else:
    for s in suggestions:
        st.write(s)

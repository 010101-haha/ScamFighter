import streamlit as st

st.set_page_config(page_title='Footprints🐾🧾', page_icon='🐾', layout="wide", initial_sidebar_state="expanded" , menu_items=None)

#st.title("The law sometimes sleeps, but the law never :blue[does] ⚖️")
new_title = '<p style="font-family:sans-serif; color:Black; font-size: 30px; font-weight:bold;">United Against <span style="color:red;">Scams</span> ⚖️</p>'
st.markdown(new_title, unsafe_allow_html=True)
#st.markdown('--')

from PIL import Image
import streamlit as st

# Load and resize the image
image = Image.open('images/cybercrime.jpg')
# Resize only if necessary
# image = image.resize((800, 300))
st.image(image, width=800)

# Markdown content with fixed paths and emojis for visuals
st.markdown("""

### Together, We Shape a Safer Digital World 🌍
##### Join the movement to fight against cybercrime and foster a just, peaceful society.
---

## 🌟 Mission Statement

#### <span style="color:red;"> **Criminals use human psychology traits, Internet, and technology as tools for manipulation, theft, and robbery, profiting off the hard-earned money of innocent individuals without facing legal consequences.** </span>

We believe that while each of us may feel powerless against multinational fraud syndicates, **collectively, we form a formidable force**. Our mission is to fight for justice, protect innocent people, and eradicate cybercrime.

---

## 🌈 Our Vision
A society that thrives on **justice, love, and peace** — where every individual feels safe and empowered online.

---

## 🔥 Our Approach

1. **People Power**: Form the Power of Governance of We, The People  
   _Taking charge and creating a community-driven governance model to ensure safety and transparency._

2. **Crowd Wisdom**: Harness the Wisdom of Our Crowd  
   _Using shared knowledge to educate, inform, and protect against scams._

3. **Collective Strength**: Leverage Our Collective Strength  
   _United, we amplify our efforts, making it harder for fraud syndicates to hide._

---

## 🌟 Why Join Us?

- **Be Part of the Solution** 🛡️: Help protect your community and loved ones.
- **Access Knowledge and Resources** 📚: Stay informed about the latest scams and prevention tactics.
- **Empower Change** 💪: Together, we can demand better security and accountability.

---

## 🚀 How You Can Help

- **Spread Awareness** 📢: Share information and insights within your network.
- **Report Scams** 📝: Your report could prevent others from falling victim.
- **Join the Community** 🌍: Engage in discussions, join forums, and collaborate in our mission.

---

### ⛓️ Together, we can transform our world for the better.

### 🔗 Together, we shape the future.

Are you ready to be part of an inspiring journey toward a cleaner, more equitable digital world?

""" , 
unsafe_allow_html=True)

# Add a final horizontal line
st.markdown("---")
st.image(Image.open('images/united-together.jpg'), width=800)
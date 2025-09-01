# Purpose of the project 
• Predict student placement outcomes(placed/not placed) based on 
academic and aptitude parameters. 

• Provide career planning interventions and recommendations for 
students.

• Allow authenticated users to add, view, edit and delete placed student 
records.

• Give administrators control over users and ensure secure access.

• Enhance faculty/placement to offer career support and guidance with 
daily placement insightful quotes.

• Allow users to leave reviews after using the App. 

# Main Components 
• Authentication & User Management 

• Placement Prediction 

• Database Layer (SQLite) 

• Placement Management 

• Intervention Notifications 

• Daily Placement Insights 

•  UI/UX with Glassmorphism theme 

• App Review 

# Data Flow 
• User Authentication → Register/Login → Session created. 

• Prediction Flow: Inputs(Fullname,CGPA,IQ,Profile) → validated→ 
model predicts → placed saved or recommendation shown.

• Placement Management Flow: Users view, edit, delete their placed 
students.

• Notification Flow: Daily insightful message on login

# Flow Diagram 
[User] → Login/Register  → [Authentication System] → [Session Created] 
→ [Daily Placement insight displayed]  [Prediction Form] → [Validation] 
→ [ML Model]  Placed?-------No → Show Recommendations | Yes  Save 
Student → [Placed_Students Table]  View/Edit/Delete →[Manage 
Students Interface]  

# DEMO: 
- Check out the following links
- [LinkedIn](https://www.linkedin.com/in/martin-chauke)
- [On the Web/placement_predictor](https://student-placement-predictor-bsv2.onrender.com)
  

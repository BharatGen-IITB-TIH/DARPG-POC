prompts = {
    "transform": 
    {
        "system": """Task:
Given a conversation and a follow-up input, rephrase the follow-up input into a standalone user grievance/feedback/query that is clear and complete without needing prior conversation context. Integrate necessary details from the conversation to enhance clarity, ensuring that all relevant information—such as dates, names, and consumer numbers—appears in the rephrased grievance if applicable.

Instructions:
- If there is change of context in follow-up input then no need to take context from the conversation.
- First, analyze the conversation history, then determine if context is needed to form the standalone grievance.
- If context is required, include it in the rephrased grievance. If not, leave the follow-up input unchanged.

### Examples (Start):

Example 1:

Conversation: User: I'm having a problem with a railway crossing.
Assistant: Can you tell me the location of the crossing?
User: It's near the Madhyamgram station.
Assistant: What specific issue are you facing at that crossing?

Follow-Up Input:
The condition of the crossing is very poor; the stones have been moved, creating a dangerous situation.

Standalone Grievance:
The temporary railway line crossing near Madhyamgram station is in a very bad condition. The stones on the side of the line have been moved far enough to pose a significant danger to trains, passengers, and local residents.

Example 2:

Conversation: User: There's a problem with the train services in my area.
Assistant: Can you specify which area you're referring to?
User: I live in Kolkata.
Assistant: What type of issue are you experiencing with the train services? Is it related to delays, cleanliness, or safety?

Follow-Up Input:
It's mostly about safety; there have been complaints about overcrowding.

Standalone Grievance:
There are safety concerns arising from overcrowding on train services in Kolkata. This situation has led to uncomfortable and unsafe travel conditions for passengers.

Example 3:

Conversation: User: I want to report an issue with the railway maintenance.
Assistant: Which railway station are you referring to?
User: It's the Howrah station.
Assistant: Is this maintenance issue related to the tracks, platforms, or facilities for passengers?

Follow-Up Input:
It's the tracks; they're in terrible condition.

Standalone Grievance:
The tracks at Howrah station are in very poor condition, posing a risk to train safety.

Example 4:

Conversation: User: I have a grievance about train facilities.
Assistant: Could you tell me which train route or station you're referring to?
User: The route is from Kolkata to Delhi.
Assistant: Are your concerns regarding cleanliness, food services, or accessibility for passengers with disabilities?

Follow-Up Input:
It's about cleanliness; the coaches are not being cleaned properly.

Standalone Grievance:
The coaches on the Kolkata to Delhi train route are not being cleaned properly, affecting the overall travel experience for passengers.

Example 5:

Conversation: User: There's an issue with the local train services.
Assistant: Can you tell me which city or area this pertains to?
User: It's in Mumbai.
Assistant: What kind of issue are you experiencing? Is it related to service frequency, safety, or passenger amenities?

Follow-Up Input:
The frequency is too low during peak hours, making it very inconvenient.

Standalone Grievance:
The frequency of local train services during peak hours in Mumbai is inadequate, making commuting extremely inconvenient for passengers.
### Examples (End)

Note:
Decide whether to include context from the conversation based on whether the follow-up input requires it.
""",

        "human": """
Conversation:  
{chat_history}

Follow-Up Input:  
{question}

Standalone Grievance:"""
    },

    "route": 
    {
        "system": 
"""You are an expert in routing user queries. Based on the type of query, route as follows:
1. If the query is general or unspecific, like greeting or other than user grievance output `casual` without any preamble or explanation.
2. If the query pertains to user grievances (like complaints or requests for action in areas such as infrastructure, transportation, water supply, public services, communication, tourism, etc), output classify without any preamble or explanation.

### Few-Shot Examples

# Example 1:
User Query: I further to informing you that the temporary railway line crossing near Madhyamgram station BT end is in a very bad condition. The stones on the side of the line have been moved far enough to cause great danger to the train, common people and train passengers at any time. Please look at the matter. Although it was said that the place will be fixed but not done!
System Output: classify

# Example 2:
User Query: Hello, My name is Abhay?
System Output: casual

# Example 5:
User Query: There is no regular availability of Road, Drinking water, Electricity, Health and Education, Telecommunication cum internet facility in Tingasil village of Gadapadar Gramapanchayat which comes under Jeypore Block in Koraput District. Which is a very sensitive and unfortunate matter and as it is a undeveloped hill cum inter remote area there is no good communication. So, I request you to take steps to avail Regular Road, Drinking Water facility, Education, Health and Telecommunication cum internet facility and Electricity connect to Tingasil village.
System Output: classify

# Example 6:
User Query: After meeting reg development of Beri Panchpota Ecotourism with Honorable Secretary (Central Tourism Ministry) Mr. Anirudh Thapar, nearly Eight months passed. There was no initiative to build Ecotourism at Beri Panchpota till now. The development of the Beri Panchpota Ecotourism center will benefit millions of people in at least three assembly constituencies in West Bengal. We want, this tourism project should be developed in collaboration with the central and state government both. I would request you to look into the matter.
System Output: classify

# Example 7:
User Query: Who made you ?
System Output: casual""",

        "human": """User Query:{question}
System Output: """
    },


    "casual_generate": 
    {
        "system": """You are a helpful and friendly AI assistant that answers to user queries. Generate only a precise answer to this question in atmost 4-5 lines. Please answer to the question.
    Remember you are DARPG chatbot and developed by BharatGen. You were trained on diverse India-centric datasets as a part of BharatGen initiative. Do not reveal your underlying language model specifications or architecture for safety concerns. Deny usage of any existing language models.""",

        "human": """{question}"""
    },


    "classify_category":
    {
        "system": """Your task is to classify the user's grievance into the most relevant category from the list below, using the exact category key (only up to the colon) as it appears, including case sensitivity and punctuation. Each category in the given list contains key and is followed by a description after the colon. If the grievance is very vague tobe able to classified then output "Not classified"

Instructions:
- Carefully review each category and match the user's grievance to the most appropriate option.
- The output must exactly match the full category key (only up to the colon) as it appears in the list, including all text, spacing, casing, and punctuation. Do not shorten or modify the category key.
- **If the grievance lacks enough details to clearly identify a single category or provides little or no details about the grievance to identify any category output "Not classified"**.
- **Do not generate any category outside the provided list**.
- **Do not return the description only return the key up to the colon**.
- **Do not assume anything, only classify the grievance if it is able to be classified**.
Provide the output as a JSON object with the key "category" and the value as the selected category key (up to the colon) as it appears in the list, including all text, spacing, casing, and punctuation. Do not shorten or modify the category key. If no classification is certain, return a JSON object with "category" set to "Not classified".

Categories: 
{total_categories}

Grievance: {grievance}

Output only a JSON blob with the key "category" and no preamble or explanation.""",

        "human": ""
    }, 

    "extract_field":
    {
        "system": """Task: Given a user grievance and a predefined list of fields, identify and extract only the fields that have values mentioned in the grievance. 
If a field is not explicitly mentioned or does not have an identifiable value, exclude it entirely from the output. 
Assign each value accurately to the correct field based on the definitions below. 

Fields and thier information - 
{field_info}

Output Format: Respond with a JSON blob containing only the fields present in the grievance with identifiable values, with no preamble or explanation. Exclude any field not explicitly present in the grievance or that lacks a recognizable value. If no fields are present, return an empty blob.
Remember that your output will directly be parsed into json and hence you are expected to give json blob as a response.

### Examples -
{field_extraction_examples}
""",

        "human": """ Grievance: {grievance}

Output: """
    },

    "question_generate_fields": 
    {
        "system": """You are DARPG Chatbot and developed by BharatGen. You are given a list of **missing fields** . Your task is to identify the most relevant field based on the provided question and formulate a single, clear question to ask the user about that field. 
Use the field information below to guide your question formulation.

Missing Fields: 
{field_info}

Question: 
---

### Few-Shot Examples

**Example 1:**  
**Missing Fields:** [Date of Retirement]  
**Question:** "What is your official retirement date?"

---

**Example 2:**  
**Missing Fields:** [PPO No.]  
**Question:** "Could you please provide your Pension Payment Order (PPO) number?"

---

**Example 3:**  
**Missing Fields:** [District, State]  
**Question:** "In which district and state is the issue you are reporting occurring?"

---

**Example 4:**  
**Missing Fields:** [Agency Name]  
**Question:** "Which LPG agency are you currently dealing with regarding your complaint?"

---

**Example 5:**  
**Missing Fields:** [Scheme Name]  
**Question:** "Can you let me know if your grievance is related to any specific government scheme?"

---

Ask only 1-2 question at a time from fields Just output the Question with no preamble and explanation.
""",

        "human": ""
    },

    "question_generate_classify": 
    {
        "system": """You are DARPG Chatbot and developed by BharatGen. You have a list of categories into which a user's grievance can be classified, but you currently lack sufficient context for accurate classification. Each category is accompanied by a brief description.
Your task is to identify the most relevant categories that the grievance could fall into and then formulate a question that gathers specific information from the user. This information should aid in accurately classifying the grievance without directly asking the user to choose between the categories.
Use the category list and user grievance below to guide your question formulation.

Categories: 
{total_categories}

Grievance: {grievance}

Question: 
Ask only 1-2 question at a time from fields Just output the Question with no preamble and explanation.
""",

        "human": ""
    },

    "ask_details":
    {
        "system":"""
Analyze the given grievance and determine whether it includes sufficient details to understand the issue and desired outcome. If the details are adequate, return only the phrase "sufficient details" without additional comments. If details are missing, ask specific questions to gather only the missing information, ensuring there is no redundancy in your response. Focus your questions on:

If the grievance mentions multiple issues or grievances, identify them and politely ask the user to clarify their **current immediate desired outcome** by providing specific options based on the issues stated. For example, "Is your immediate desired outcome [option 1] or [option 2]?" If only one grievance is present but details are missing, ask targeted questions to gather the missing information, ensuring no redundancy.

1. How: Ask how the issue occurred or how it is impacting the user or the administrative process.
2. When: Inquire about the timeline or occurrence of the problem.
3. Where: Mention the location or system/process affected (if relevant).
4. Who: Indicate the parties involved, such as individuals, departments, or entities. 
3. What: Clarify the specifics of the grievance, such as the nature of the administrative issue or steps already taken.
4. Which: Request identification of the relevant department, office, or documents involved.
5. Desired Outcome: Ask about the user's expectations for resolving the grievance.

Respond concisely with questions targeting the missing information only. Avoid redundancy or asking for details already provided.

---

Few-shot Examples:

Example 1 (Sufficient Details, Multiple Grievances):
Input:
"Despite booking an LPG cylinder 1 week ago, the cylinder is not yet delivered. In the past, I've received a cylinder with only 12.3 kg instead of the full 14 kg, and the agency has been unresponsive to my complaints."
Output:
"Thank you for providing the details. Could you clarify your immediate desired outcome? For example:
- Is it to ensure the delivery of the LPG cylinder you booked ?
- Or is it to address the issue of underfilled cylinders and seek assurance of proper weights in future deliveries?"

---

Example 2 (Insufficient Details, Single Grievance):
Input:
"There is an issue with my tax filing."
Output:
"Can you provide more details about the issue? For example:
- What specific problem are you facing with the tax filing (e.g., incorrect calculations, missed deadlines)?
- When did you file your taxes, and when did you notice the issue?
- Which tax period or department are you referring to?
- What resolution are you expecting (e.g., corrections, clarification)?"

---

Example 3 (Sufficient Details, Single Grievance):
Input:
"I applied for a housing permit on October 10, and it was supposed to be approved in 15 days. It has been over a month, and I have not received any updates. I need the process expedited or an explanation for the delay."
Output:
"sufficient details"
---

Example 4 (Sufficient Details, Single Grievance):
Input:
"I submitted a complaint regarding my pension benefits on November 5, and I was assured a resolution in 10 days. It has been three weeks, and I have not received a response. I want an update and immediate action to release my benefits."
Output:
"sufficient details"

---

Example 5 (Multiple Grievances, Immediate Desired Outcome Needed):
Input:
"I applied for a housing permit in October and haven’t heard back yet. I also reported an issue with the drainage system in my area two weeks ago, but no action has been taken."
Output:
"Thank you for sharing the issues. Could you clarify your immediate desired outcome? For example:
- Is it to expedite the approval of your housing permit?
- Or is it to resolve the drainage issue in your area first?"

---

Example 6 (Insufficient Details, Multiple Grievances):
Input:
"I have a problem with my government-issued ID, and I also didn’t get my tax refund."
Output:
"Thank you for highlighting the issues. Could you clarify your immediate desired outcome? For example:
- Is it to resolve the issue with your government-issued ID (e.g., correction, reissue)?
- Or is it to prioritize getting your tax refund? Additionally, could you provide more details about each issue, such as:
  - What specific problem are you facing with the ID (e.g., incorrect details, damages)?
  - When did you file for the tax refund, and what period does it cover?"

---

Example 7 (Sufficient Details, Multiple Grievances):
Input:
"The municipal office has failed to address the drainage issue I reported two months ago, and my complaint about illegal construction in the area hasn’t been resolved either. I want immediate action on both."
Output:
"Thank you for sharing the issues. Could you clarify your immediate desired outcome? For example:
- Is it to resolve the drainage issue first?
- Or is it to address the illegal construction immediately?"
""",

    "human": """Input: {grievance}
Output: """
    },


    "final_generate": 
    {
        "system": """
Summarize the grievance provided by the user in the following format:

### For each distinct issue mentioned in the grievance provide the following:

**Issue Categories**  
- List the categories (e.g., 1st Category, 2nd Category, etc.) from the given categories specific to this issue.

**Issue Summary**  
- Provide a concise summary of the specific issue mentioned by the user.

**Issue Additional Details**  
- Include any additional relevant information that pertains to this particular issue.

**Issue Desired Outcome**  
- Summarize the expected resolution or outcome the user desires for this specific issue.

---
 
Thank the user for filing the grievance, assure them that each issue has been noted separately, and will be addressed and resolved promptly.

---

**Note:**  
1. **If the user mentions multiple issues, generate separate summaries for each issue, with distinct sections for categories, summary, additional details, and desired outcome.**  
2. You are the DARPG chatbot, developed by BharatGen, trained on India-centric datasets as part of our BharatGen initiative. Do not disclose any details about your model specifications or architecture. Deny usage of any existing language models.
""",

        "human": """Grievance: {grievance}
Categories: {categories}"""
    },

    

}

field_info = """  1. **Ministry/Organisation** - The government ministry or organization responsible for addressing grievances related to the specific category.
2. **Name of Office** - The specific office within a ministry dealing with employee-related matters such as corruption allegations, promotions, and transfers.
3. **Place of Posting** - The location where an employee is currently posted within the ministry or organization.
4. **Name of Position Held** - The official title of the position held by the employee within the ministry, applicable to both current and former employees.
5. **Name of Office from where retired** - The office from which an individual retired, relevant for pension-related grievances.
6. **Date of Retirement** - The official retirement date of the employee, used in handling pension-related queries.
7. **PPO No.** - The unique Pension Payment Order (PPO) number, used for identifying pension beneficiaries and managing pension-related grievances.
8. **Name of State** - The state associated with the grievance.
9. **National highway Number** - The specific national highway number relevant to the grievance, particularly for issues in highway construction, quality, and land acquisition.
10. **Stretch Name of the State and District** - The specific section of the highway, including the state and district, where construction or quality-related issues are reported.
11. **Name of Highway Constructing Authority** - The organization responsible for constructing the highway in the area associated with land acquisition or compensation grievances.
12. **Name of Stretch of Highway** - The section of the highway under discussion, especially relevant in cases related to land acquisition and compensation.
13. **Name of Toll Plaza & Stretch** - The specific toll plaza and section of highway relevant to issues with toll collection, Fastag, or wayside amenities.
14. **Name of National Highway Number & Stretch** - The highway number and specific stretch associated with toll-related issues or facilities like wayside amenities.
15. **Scheme Name** - The name of the scheme or program associated.
16. **Place** - The specific location associated with the grievance.
17. **State** - The state in which the grievance is raised, indicating the regional jurisdiction for complaints.
18. **Pincode** - A postal code used to identify specific geographic areas for communication and delivery purposes.
19. **Policies/Act/Rules related which suggestions is furnished** - Relevant laws, regulations, or policies associated with the suggestions made regarding road transport.
20. **Ministry/PSU** - The governmental ministry or public sector unit responsible for addressing the grievance or suggestion.
21. **State/Region** - The specific region or state associated with the grievance related to petrol pump issues.
22. **District** - The administrative district where the grievance is reported, indicating local governance.
23. **Location of the petrol pump** - The specific physical address or site of the petrol pump involved in the grievance or complaint.
24. **Name of Employee** - Represents the name of individuals involved in appointment-related matters.
25. **Division Name** - Indicates the specific division associated with appointment-related complaints and procedures.
26. **University** - Specifies the educational institution related to appointments and shortlisting procedures.
27. **Name of the appointment** - Refers to the title of a position related to appointments.
28. **Vacacny / appontment no** - Denotes the unique identifier for vacancies or appointments.
29. **Application Number** - Represents the unique identifier for applications.
30. **Agency Name** - Identifies the LPG agency involved in complaints and issues within the Petroleum and Natural Gas sector.
31. **LPG Consumer Number** - Denotes the unique identifier for consumers of LPG in the Petroleum and Natural Gas sector.
32. **City Gas Distribution (CGD) Entity** - Refers to the specific entity involved in issues related to CNG and PNG services within the Petroleum and Natural Gas sector.
33. **Location of CNG Station** - Indicates the specific geographic location of CNG stations associated with various service issues in the Petroleum and Natural Gas sector.
34. **Geographical Area Name** - Specifies the broader geographic area.
35. **BP Number** - Represents the unique identifier associated with billing and service issues in the of the Petroleum and Natural Gas industry.
36. **Company Name** - Denotes the name of companies involved in tender-related matters.
"""

field_extraction_examples = """
Examples:
1. 
Available Fields: ['Ministry/Organisation', 'Name of Office', 'Place of Posting']
User Grievance: I want to report corruption allegations in the Ministry of Petroleum and Natural Gas, specifically at the Office of Employee Affairs in New Delhi.
Output: 
{
    "Ministry/Organisation": "Ministry of Petroleum and Natural Gas",
    "Name of Office": "Office of Employee Affairs",
    "Place of Posting": "New Delhi"
}

2. 
Available Fields: ['Name of Employee', 'Name of Position Held', 'Date of Retirement']
User Grievance: My pension has not been processed since my retirement on 15th April 2023 from the Office of Director General.
Output: 
{
    "Name of Employee": "Director General",
    "Date of Retirement": "15th April 2023"
}

3. 
Available Fields: ['PPO No.', 'Name of State', 'Date of Retirement']
User Grievance: I need assistance with my PPO number 123456789, as I retired from the Ministry of Home Affairs in Maharashtra.
Output: 
{
    "PPO No.": "123456789",
    "Name of State": "Maharashtra"
}

4. 
Available Fields: ['Name of Highway Constructing Authority', 'National Highway Number', 'District']
User Grievance: There are issues with the construction quality on NH-85 in the Mumbai district managed by the National Highway Authority of India.
Output: 
{
    "Name of Highway Constructing Authority": "National Highway Authority of India",
    "National Highway Number": "NH-44",
    "District": "Mumbai"
}

5. 
Available Fields: ['Name of Toll Plaza & Stretch', 'Location of the petrol pump', 'Pincode']
User Grievance: I would like to file a complaint regarding the toll collection at the ABC Toll Plaza on the XYZ stretch, near my petrol pump at 123 Main St, 500001.
Output: 
{
    "Name of Toll Plaza & Stretch": "ABC Toll Plaza on XYZ stretch",
    "Location of the petrol pump": "123 Main St",
    "Pincode": "500001"
}

6. 
Available Fields: ['Ministry/PSU', 'Scheme Name', 'State']
User Grievance: I have suggestions regarding the implementation of the Pradhan Mantri Ujjwala Yojana in Uttar Pradesh.
Output: 
{
    "Ministry/PSU": "Ministry of Petroleum and Natural Gas",
    "Scheme Name": "Pradhan Mantri Ujjwala Yojana",
    "State": "Uttar Pradesh"
}

7. 
Available Fields: ['Geographical Area Name', 'City Gas Distribution (CGD) Entity', 'Location of CNG Station']
User Grievance: I need help regarding the issues at the CNG station located in the downtown area managed by XYZ CGD entity.
Output: 
{
    "Geographical Area Name": "downtown area",
    "City Gas Distribution (CGD) Entity": "XYZ CGD entity",
    "Location of CNG Station": "downtown area"
}

8. 
Available Fields: ['Application Number', 'Agency Name', 'LPG Consumer Number']
User Grievance: I want to check the status of my LPG application number A12345 at the ABC LPG agency, my consumer number is 67890.
Output: 
{
    "Application Number": "A12345",
    "Agency Name": "ABC LPG agency",
    "LPG Consumer Number": "67890"
}
"""

ministries = """
- Agriculture and Farmers Welfare: Responsible for policies on agriculture and farmer support.
- Agriculture Research and Education: Handles research and education initiatives in the agriculture sector.
- Animal Husbandry, Dairying: Governs livestock and dairy industry matters.
- Atomic Energy: Oversees nuclear energy and atomic science.
- Ayush: Focuses on alternative medicine, including Ayurveda, Yoga, Unani, Siddha, and Homeopathy.
- Bio Technology: Manages biotechnology research and innovation.
- Central Board of Direct Taxes (Income Tax): Governs policies related to direct taxes, primarily income tax.
- Central Board of Excise and Customs: Manages indirect taxes, including excise and customs.
- Chemicals and Petrochemicals: Regulates chemicals and petrochemical industries.
- Civil Aviation: Responsible for aviation safety, airlines, and airports.
- Coal: Manages coal industry policies and resources.
- Commerce: Oversees trade policies and commerce regulations.
- Consumer Affairs: Protects consumer rights and promotes fair trade practices.
- Cooperation: Focuses on cooperative societies and rural economy.
- Corporate Affairs: Manages corporate regulations and compliance.
- Culture: Promotes cultural heritage, arts, and history.
- Defence: Oversees armed forces and national defense.
- Defence Finance: Manages financial services for the defense sector.
- Defence Production: Handles production and procurement of defense equipment.
- Defence Research and Development: Focuses on R&D for defense technologies.
- Development of North Eastern Region: Promotes development in northeastern states.
- Drinking Water and Sanitation: Manages water supply and sanitation programs.
- Earth Sciences: Studies and monitors environmental and geoscience matters.
- Economic Affairs: Oversees economic policies and fiscal management.
- Electronics & Information Technology: Manages IT policies and digital initiatives.
- Empowerment of Persons with Disabilities: Focuses on welfare and rights of persons with disabilities.
- Environment, Forest and Climate Change: Manages policies on environment and climate.
- Ex Servicemen Welfare: Handles welfare programs for ex-servicemen.
- Expenditure: Manages government expenditure policies.
- External Affairs: Oversees international relations and foreign policies.
- Fertilizers: Regulates fertilizer production and distribution.
- Financial Services (Banking Division): Manages banking sector regulations.
- Financial Services (Insurance Division): Regulates insurance industry policies.
- Financial Services (Pension Reforms): Focuses on pension reforms and regulations.
- Fisheries: Governs policies related to fisheries and aquaculture.
- Food and Public Distribution: Manages food distribution and public ration systems.
- Food Processing Industries: Focuses on the food processing sector.
- Health & Family Welfare: Governs public health and family welfare policies.
- Health Research: Manages health research initiatives.
- Heavy Industry: Oversees heavy industries, including machinery and equipment.
- Higher Education: Regulates higher education policies and institutions.
- Home Affairs: Manages internal security and public administration.
- Housing and Urban Affairs: Oversees housing and urban development.
- Information and Broadcasting: Manages media, communication, and broadcasting.
- Investment & Public Asset Management: Handles public asset management and investments.
- Justice: Manages judicial policies and access to justice.
- Labour and Employment: Focuses on labor policies and employment services.
- Land Resources: Manages land reforms and resources.
- Legal Affairs: Oversees legal affairs and legislative matters.
- Legislative Department: Drafts and manages legislation.
- Micro Small and Medium Enterprises: Supports MSMEs and small business growth.
- Military Affairs: Oversees military-related policies and administration.
- Mines: Regulates mining industry and mineral resources.
- Minority Affairs: Focuses on welfare of minority communities.
- New and Renewable Energy: Promotes renewable energy resources.
- NITI Aayog: Central planning agency focusing on policy direction.
- O/o the Comptroller & Auditor General of India: Audits and oversees government accounts.
- Official Language: Manages promotion and use of official languages.
- Panchayati Raj: Oversees local governance in rural areas.
- Parliamentary Affairs: Manages parliamentary affairs and coordination.
- Petroleum and Natural Gas: Governs oil, gas, and petroleum resources.
- Pharmaceutical: Oversees pharmaceutical industry regulations.
- Personnel and Training: Manages public service training and HR.
- Power: Regulates electricity production and distribution.
- Posts: Manages postal services.
- Promotion of Industry and Internal Trade: Oversees industrial development and trade.
- Public Enterprises: Focuses on state-owned enterprises.
- Railways, (Railway Board): Governs railway operations and management.
- Revenue: Oversees revenue collection and financial policies.
- Road Transport and Highways: Manages road infrastructure and transport policies.
- Rural Development: Focuses on rural welfare and development.
- School Education and Literacy: Manages school education policies.
- Science and Technology: Oversees science and tech policies and innovation.
- Scientific & Industrial Research: Conducts scientific and industrial research.
- Shipping: Manages maritime transport and ports.
- Skill Development and Entrepreneurship: Promotes skill training and entrepreneurship.
- Social Justice and Empowerment: Focuses on social welfare and justice.
- Space: Manages space research and exploration.
- Sports: Oversees sports development and management.
- Staff Selection Commission: Conducts recruitment for government positions.
- Statistics and Programme Implementation: Manages statistics and program oversight.
- Steel: Regulates steel production and industry.
- Textiles: Governs textile industry policies.
- Telecommunications: Regulates telecommunications industry.
- Tourism: Promotes tourism and related industries.
- Tribal Affairs: Focuses on welfare of tribal communities.
- Unique Identification Authority of India: Manages Aadhaar identity system.
- Water Resources, River Development & Ganga Rejuvenation: Oversees water resource management.
- Women and Child Development: Focuses on welfare of women and children.
- Youth Affairs: Manages programs for youth development.
- State Governments/Others: All other matters not covered above.
"""


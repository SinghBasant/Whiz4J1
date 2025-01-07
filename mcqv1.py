import openai
import streamlit as st
import re
# from dotenv import load_dotenv
# import os

# Load environment variables
# load_dotenv()

# Set your OpenAI API key
openai.api_key = st.secrets["OPEN_AI_KEY"]

# Streamlit UI
st.title("WhizCoach :sunglasses: Interactive Practice with Validation")

st.sidebar.header("Powered by Whizlabs R&D")
st.sidebar.write("""
1. Enter a topic and the number of MCQs (<=20) to generate.
2. Select your answers.
3. Submit your answers to validate them.
4. You can practice with any topic: example > Generate CBSE Math linear equation word problems for grade 8th India.
5. It's a POC - don't expect corner cases to be handled :-)
""")

# Input: Topic and number of questions
topic = st.text_input("Enter the topic for MCQs:", "Generate practice questions for AWS Certified AI Practitioner exam")
num_questions = st.number_input("Number of MCQs to generate:", min_value=1, max_value=20, value=5)

if st.button("Generate MCQs"):
    with st.spinner("Generating MCQs..."):
        try:
            # OpenAI API call to generate MCQs
            prompt = f"""
Generate {num_questions} multiple-choice questions (MCQs) on the topic "{topic}".
Each question should include 4 options and clearly indicate the correct answer. Format the response as:
1. Question text
    a) Option 1
    b) Option 2
    c) Option 3
    d) Option 4
    Correct Answer: (letter corresponding to the correct answer)
"""
            #response = openai.ChatCompletion.create(
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )

            # Parse response
            #generated_mcqs = response['choices'][0]['message']['content'].strip().split("\n\n")
            generated_mcqs = response.choices[0].message.content.strip().split("\n\n")  
            st.session_state.mcqs = []

            for mcq in generated_mcqs:
                lines = mcq.split("\n")
                if len(lines) >= 6:  # Ensure valid structure (1 question + 4 options + 1 answer line)
                    question = lines[0].strip()
                    options = [line.strip() for line in lines[1:5]]

                    # Extract the correct answer using regex
                    answer_match = re.search(r"Correct Answer: ([a-dA-D])", lines[5])
                    if answer_match:
                        correct_letter = answer_match.group(1).lower()
                        if ord(correct_letter) - ord('a') < len(options):
                            correct_answer = options[ord(correct_letter) - ord('a')]
                            st.session_state.mcqs.append({
                                "question": question,
                                "options": options,
                                "correct_answer": correct_answer,
                                "user_answer": None
                            })
                        else:
                            st.warning(f"Correct answer index out of range for question: {question}")
                    else:
                        st.warning(f"Invalid answer format for question: {question}. Skipping this question.")
                else:
                    st.warning(f"Invalid format for question: {mcq}. Skipping this question.")

            if not st.session_state.mcqs:
                st.error("Failed to parse MCQs correctly. Please try again.")
            else:
                st.success("MCQs Generated Successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Display MCQs and collect user answers
if "mcqs" in st.session_state:
    st.header("Answer the MCQs")
    for idx, mcq in enumerate(st.session_state.mcqs):
        st.subheader(mcq["question"])
        mcq["user_answer"] = st.radio(f"Select your answer for Q{idx + 1}:", mcq["options"], key=f"q{idx}")

    if st.button("Submit Answers"):
        with st.spinner("Validating your answers..."):
            try:
                st.header("Results")
                score = 0
                for idx, mcq in enumerate(st.session_state.mcqs):
                    correct_option = mcq["correct_answer"]
                    user_answer = mcq["user_answer"]

                    if user_answer == correct_option:
                        st.success(f"**Q{idx + 1}:** Correct!")
                        score += 1
                    else:
                        st.error(f"**Q{idx + 1}:** Incorrect. Correct answer: {correct_option}")

                st.write(f"**Your Total Score: {score}/{len(st.session_state.mcqs)}**")

            except Exception as e:
                st.error(f"An error occurred during validation: {e}")

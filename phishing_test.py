import pandas as pd
import openai
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

# Set up OpenAI API key
openai.api_key = ""
DEMONSTRATIONS = """
Example 1:
Subject: Limited-time offer just for you!
Body: Claim your free gift by clicking here: [suspicious_link]
Label: 1

Example 2:
Subject: Meeting Reminder
Body: Your project meeting is scheduled for tomorrow at 10 AM. Please find the agenda attached.
Label: 0
"""
# Function to analyze email content with ChatGPT
def analyze_email_with_chatgpt(email_content):
    prompt = f"""
    You are an email classification expert. Your task is to determine whether an email is spam or not spam. Use the examples below as guidance:

    {DEMONSTRATIONS}

    Now analyze the following email:

    Email Content:
    {email_content}

    Respond with '1' for spam or '0' for not spam.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
{
  "role": "system",
  "content": "You are a cybersecurity expert specializing in email analysis. Your job is to determine if an email is a phishing attempt or a legitimate message. Analyze key elements such as urgency, tone, sender details, suspicious links, and content consistency. Consider legitimate cases, such as academic invitations or corporate announcements, and avoid labeling an email as phishing unless there are clear indicators of malicious intent."
},                {"role": "user", "content": prompt}
            ]
        )
        # Extract the message content
        response_dict = response.model_dump() 
        chatgpt_response = response_dict["choices"][0]["message"]["content"].strip()
        print (chatgpt_response)
        # Check for "Phishing" in response
        if chatgpt_response.startswith('1'):
            return 1
        elif chatgpt_response.startswith('0'):
            return 0
        else:
            print(f"Unexpected response format: {chatgpt_response}")
            return None
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None


# Load and preprocess the dataset
def load_dataset(file_path, sample_size=None):
    # Load the dataset
    df = pd.read_csv(file_path)
    
    if "text_combined" not in df.columns or "label" not in df.columns:
        raise ValueError("Dataset must contain 'text_combined' and 'label' columns.")
    
    # Convert labels to integers
    df['label'] = df['label'].astype(int)
    
    # Sample the dataset if specified
    if sample_size:
        df, _ = train_test_split(df, test_size=1 - sample_size / len(df), stratify=df['label'], random_state=42)
    
    return df


# Calculate accuracy and other metrics
def calculate_metrics(df):
    # Filter out invalid predictions
    df = df[df['ChatGPT_Analysis'].notnull()]
    df['ChatGPT_Analysis'] = df['ChatGPT_Analysis'].astype(int)

    # Ensure required columns exist
    if "ChatGPT_Analysis" not in df.columns or "label" not in df.columns:
        raise ValueError("Dataset must contain 'ChatGPT_Analysis' and 'label' columns.")

    # Print classification report
    print("\nChatGPT Performance Metrics:")
    print(classification_report(df['label'], df['ChatGPT_Analysis'], target_names=["Not Spam", "Spam"]))


# Process the dataset and evaluate emails
def evaluate_dataset(file_path, output_file, sample_size=None):
    # Load the dataset
    df = load_dataset(file_path, sample_size=sample_size)
    
    # Add a column for ChatGPT's analysis
    df['ChatGPT_Analysis'] = None
    
    # Iterate through the dataset and analyze emails
    # Iterate through the dataset and analyze emails
    for index, row in df.iterrows():
        print(f"Analyzing email {index + 1}/{len(df)}...")
        email_content = row['text_combined']
        analysis = analyze_email_with_chatgpt(email_content)
        df.at[index, 'ChatGPT_Analysis'] = analysis
        print(f"Result for email {index + 1}: {'Spam' if analysis == 1 else 'Not Spam'}")

    # Save the results to a new CSV file
    df.to_csv(output_file, index=False)
    print(f"Analysis completed. Results saved to {output_file}")
    
    # Calculate accuracy and print it
    calculate_metrics(df)

if __name__ == "__main__":
    # Path to the dataset
    dataset_path = "phishing_email.csv"
    
    # Output file for results
    output_path = "chatgpt_phishing_analysis.csv"
    
    # Number of samples to test
    sample_size = 100 # Process only 1000 emails for testing
    
    # Run the evaluation
    evaluate_dataset(dataset_path, output_path, sample_size=sample_size)

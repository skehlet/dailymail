import os
import json
import boto3
from pydantic import BaseModel

# Environment variables
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-haiku-20241022-v1:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-west-2")
BEDROCK_CONTEXT_WINDOW_SIZE = int(os.getenv("BEDROCK_CONTEXT_WINDOW_SIZE", "200000"))

# Pydantic model to ensure consistent return type with your OpenAI implementation
class TextSummary(BaseModel):
    """
    TextSummary object returned by the model, parsed from the response.
    """
    summary: str
    notable_aspects: str
    relevance: str
    relevance_explanation: str


# Initialize Bedrock client
client = boto3.client(
    "bedrock-runtime",
    region_name=BEDROCK_REGION
)


def get_model_id():
    """Return a string with the model ID for logging"""
    return f"{BEDROCK_MODEL_ID} (AWS Bedrock)"


def summarize_text(url, title, text):
    """
    Summarize a text article using Claude 3.5 Haiku via Bedrock Converse API.
    
    Args:
        url (str): The source URL of the text
        title (str): The title of the article
        text (str): The content to be summarized
        
    Returns:
        TextSummary: Structured summary of the text
    """
    
    # This prompt follows Claude's format expectations and mirrors your OpenAI prompt
    prompt = """
Your task is to analyze news articles and provide concise, relevant summaries highlighting key information.

STEP 1: RELEVANCE DETERMINATION
Determine if the article is 'RELEVANT' or 'NOT RELEVANT' based on these criteria:

RELEVANT content:
- Contains substantive news, analysis, or information about current events, trends, or developments
- Presents original reporting, research findings, or expert perspectives
- Offers meaningful insights or data points that would inform a reader about the world
- Example: "Federal Reserve raises interest rates by 0.5%, citing persistent inflation concerns and strong labor market data."

NOT RELEVANT content:
- Platform announcements (e.g., "This article is hosted on Substack")
- Subscription solicitations or marketing content
- Purely administrative text (e.g., "Thanks for reading," "Subscribe to our newsletter")
- Website navigation information, user agreements, or generic platform descriptions
- Example: "Support independent journalism by becoming a paid subscriber. Unlock exclusive content and join our community."

STEP 2: FOR RELEVANT CONTENT ONLY
Summary (3-4 sentences):
- Begin directly with the most important information
- Include key facts, figures, and central claims
- Present complete thoughts without referencing the article itself
- Preserve accuracy without editorializing

Notable Aspects (1-2 points):
- Highlight unexpected information, unique perspectives, or important implications
- Focus on elements that add depth beyond the main summary
- Identify potential consequences, historical context, or statistical outliers worth attention
"""
    
    # Shorten text to fit context window
    shortened_text = text[:BEDROCK_CONTEXT_WINDOW_SIZE - len(prompt) - 1000]  # Extra buffer
    
    # Format input for the article to summarize
    article_info = f"""
URL: {url}
Title: {title}
Content: {shortened_text}
"""
    
    # Define the tool schema for structured output
    tool_list = [
        {
            "toolSpec": {
                "name": "deliver_summary",
                "description": "Deliver the summary of the article",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "3-4 sentence summary that captures key ideas and essential information"
                            },
                            "notable_aspects": {
                                "type": "string",
                                "description": "1-2 sentences highlighting unique or surprising information"
                            },
                            "relevance": {
                                "type": "string",
                                "description": "RELEVANT or NOT RELEVANT"
                            },
                            "relevance_explanation": {
                                "type": "string",
                                "description": "Brief explanation of relevance determination"
                            }
                        },
                        "required": ["summary", "notable_aspects", "relevance", "relevance_explanation"]
                    }
                }
            }
        }
    ]
    
    # Set up conversation messages
    messages = [
        {
            "role": "user",
            "content": [
                {"text": prompt},
                {"text": article_info}
            ]
        }
    ]
    
    # Make API call to Bedrock
    response = client.converse(
        modelId=BEDROCK_MODEL_ID,
        messages=messages,
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0
        },
        toolConfig={
            "tools": tool_list,
            "toolChoice": {"tool": {"name": "deliver_summary"}}
        }
    )
    
    # Extract the tool use from the response
    content_blocks = response["output"]["message"]["content"]
    tool_use_block = None
    
    for block in content_blocks:
        if "toolUse" in block:
            tool_use_block = block["toolUse"]
            break
    
    if not tool_use_block:
        raise Exception("No tool use found in the response")
    
    # Extract the result from the tool use
    result = tool_use_block["input"]
    
    # Create and return a dictionary
    return {
        "summary": result["summary"],
        "notable_aspects": result["notable_aspects"],
        "relevance": result["relevance"],
        "relevance_explanation": result["relevance_explanation"]
    }


def summarize_google_alert(topic, url, title, text):
    """
    Analyze text for relevance to a specific topic and provide a summary.
    
    Args:
        topic (str): The topic to check relevance against
        url (str): The source URL of the text
        title (str): The title of the article
        text (str): The content to be summarized
        
    Returns:
        TextSummary: Structured summary of the text
    """
    
    # This prompt follows Claude's format expectations and mirrors your OpenAI prompt
    prompt = f"""
Your task is to analyze the provided text for relevance to the topic specified below and, if relevant, provide a concise, actionable summary.

TOPIC: {topic}

STEP 1: RELEVANCE DETERMINATION
Determine if the text is 'RELEVANT' or 'NOT RELEVANT' based on these criteria:

RELEVANT content must:
- Directly address the full TOPIC with substantive information
- Contain specific details related to ALL quoted terms within the TOPIC (e.g., if TOPIC contains "release date" and "PC", both elements must be addressed)
- Provide actionable or informative content that would be valuable to someone tracking this specific TOPIC

NOT RELEVANT content includes:
- Text that addresses only some quoted terms from the TOPIC but not others
- Content that mentions keywords from the TOPIC without providing specific information about the quoted terms
- Articles where the TOPIC appears only in metadata, tags, or peripheral sections
- Content that discusses related themes but doesn't directly address the combination of terms in the TOPIC

STEP 2: FOR RELEVANT CONTENT ONLY
Summary (3-4 sentences):
- Begin with the most important information related specifically to the TOPIC
- Include key dates, numbers, developments, or announcements
- Focus only on information directly related to the TOPIC, omitting tangential details
- Present complete thoughts without referencing the article itself

Notable Aspects (1-2 points):
- Highlight information that would be most actionable or decision-relevant
- Focus on new developments, changes from previous information, or unexpected elements
- For topics about products/services: Include pricing, availability, or competitive positioning when available
- For topics about events/people: Include timeline information, context, or implications
"""
    
    # Format input with the article information
    text_info = f"""
Source: {url}
Title: {title}
Text: {text}
"""
    
    # Shorten text to fit context window
    max_text_length = BEDROCK_CONTEXT_WINDOW_SIZE - len(prompt) - 1000  # Extra buffer
    text_info = text_info[:max_text_length]
    
    # Define the tool schema for structured output
    tool_list = [
        {
            "toolSpec": {
                "name": "deliver_topic_summary",
                "description": "Deliver the topic-focused summary of the article",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "3-4 sentence summary related to the topic"
                            },
                            "notable_aspects": {
                                "type": "string",
                                "description": "1-2 sentences highlighting actionable or decision-relevant information"
                            },
                            "relevance": {
                                "type": "string",
                                "description": "RELEVANT or NOT RELEVANT"
                            },
                            "relevance_explanation": {
                                "type": "string",
                                "description": "Brief explanation of relevance determination"
                            }
                        },
                        "required": ["summary", "notable_aspects", "relevance", "relevance_explanation"]
                    }
                }
            }
        }
    ]
    
    # Set up conversation messages
    messages = [
        {
            "role": "user",
            "content": [
                {"text": prompt},
                {"text": text_info}
            ]
        }
    ]
    
    # Make API call to Bedrock
    response = client.converse(
        modelId=BEDROCK_MODEL_ID,
        messages=messages,
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0
        },
        toolConfig={
            "tools": tool_list,
            "toolChoice": {"tool": {"name": "deliver_topic_summary"}}
        }
    )
    
    # Extract the tool use from the response
    content_blocks = response["output"]["message"]["content"]
    tool_use_block = None
    
    for block in content_blocks:
        if "toolUse" in block:
            tool_use_block = block["toolUse"]
            break
    
    if not tool_use_block:
        raise Exception("No tool use found in the response")
    
    # Extract the result from the tool use
    result = tool_use_block["input"]
    
    # Create and return a dictionary
    return {
        "summary": result["summary"],
        "notable_aspects": result["notable_aspects"],
        "relevance": result["relevance"],
        "relevance_explanation": result["relevance_explanation"]
    }


# if __name__ == "__main__":
#     # Test the VW article summarization
#     vw_article = """
# Volkswagen and Rivian are joining forces as part of a $5.8 billion dollar deal, one that will see the two companies co-develop architectures and software for future electric vehicles. Now, one VW exec has confirmed where we'll first see the fruits of this joint development between the legacy German automaker and the U.S. startup: the next-generation Volkswagen Golf.
# According to reporting from CarSales, development of the electrified hatchback is set to start soon, and Volkswagen is seemingly excited to leverage the engineering prowess and zonal architecture of Illinois's premier electric pickup truck manufacturer. Currently in its eighth generation, the Volkswagen Golf just received a facelift for the 2025 model year, meaning the ninth-generation version of this iconic compact isn't set to arrive until 2029.
#     """
    
#     result = summarize_text(
#         "https://www.roadandtrack.com/news/a63081162/volkswagen-rivian-mk9-golf/",
#         "Volkswagen Says Rivian Will Help Develop Electric Mk9 Golf",
#         vw_article
#     )
    
#     print(json.dumps(result, indent=2))
    
#     # Test Google Alert summarization
#     result2 = summarize_google_alert(
#         "Golf Mk9",
#         "https://www.roadandtrack.com/news/a63081162/volkswagen-rivian-mk9-golf/",
#         "Volkswagen Says Rivian Will Help Develop Electric Mk9 Golf",
#         vw_article
#     )
    
#     print(json.dumps(result2, indent=2))


# Debug LLM locally
# start with something like:
# env AWS_PROFILE=kronos-unstable-dev-solutions BEDROCK_MODEL_ID=us.anthropic.claude-3-5-haiku-20241022-v1:0 BEDROCK_REGION=us-east-1 BEDROCK_CONTEXT_WINDOW_SIZE=200000 python summarize_bedrock.py
# Or my personal account:
# env AWS_PROFILE=stevek-free-tier BEDROCK_MODEL_ID=us.anthropic.claude-3-5-haiku-20241022-v1:0 BEDROCK_REGION=us-west-2 BEDROCK_CONTEXT_WINDOW_SIZE=200000 python summarize_bedrock.py
# AWS_PROFILE=stevek-free-tier BEDROCK_MODEL_ID=us.amazon.nova-micro-v1:0 BEDROCK_REGION=us-west-2 BEDROCK_CONTEXT_WINDOW_SIZE=50000 python summarize_bedrock.py
if __name__ == "__main__":
#     text = """\
# Goodbye GTX, we hardly knew thee! But Volkswagen fans needn't fret, the company is planning GTI and R versions of its next-gen electric cars.
# CommentsJoin the Convo
# Volkswagen resurrected the GTX badge to denote its heated-up electric cars, but it looks set to replace it with GTI and R variants.
# Thomas Schäfer, CEO of the Volkswagen brand, told Autocar, “GTX is the performance brand of the MEB [EV architecture], but we’ll work our way back to GTI and R in the next products going forward”.
# The change will likely take a few years to sweep through the Volkswagen EV range, with Mr Schäfer clarifying “the current products, this is what it is, but future products will go back to a clear portfolio [of GTI and R]”.
# Volkswagen gave an indication this was going to be the way forward when it unveiled the ID.GTI concept in September 2023, which is based on the earlier ID. 2all concept.
# The production version of the ID. 2all, sized between the Polo and Golf, is expected to go into production from 2025, while the front-wheel drive GTI variant should start trundling down the factory line from 2027.
# According to the Volkswagen brand’s CEO, there’s still some debate within the company about how to use the GTI and R sub-brands, principally centring on the question: “How do we position GTI?”
# According to Mr Schäfer, “GTI is traditionally performance and front-wheel drive” with the R reserved for “for four-wheel-drive performance”. He said both sub-brands would have “clear genes going forward”.
# The picture with the current selection of GTX models is a little more muddied. There are GTX versions of the ID.3 tall hatch, ID.4 crossover, ID.5 crossover coupe, and ID.Buzz people mover.
# While the ID.3 GTX is rear-wheel drive, the ID.4 GTX, ID.5 GTX and ID.Buzz GTX are all all-wheel drive.
# All GTX models have more power and torque than their lesser siblings. They also have sportier styling and retuned handling, but the changes are not as clear a leap over other models compared to GTI and R cars.
# At the time of writing, the only Volkswagen models with GTI versions are the Polo and Golf. There’s a much broader selection of R vehicles, including the Golf, T-Roc, Tiguan, and Touareg.
# Derek Fung would love to tell you about his multiple degrees, but he's too busy writing up some news right now. In his spare time Derek loves chasing automotive rabbits down the hole. Based in New York, New York, Derek loves to travel and is very much a window not an aisle person.
# Learn about CarExpert or
# 17 hours agoThis V12 manual hypercar proves electric isn't the only way
# 22 hours agoWhat should you buy instead of a Tesla Model Y?"""

#     text = """\
# We tried to load scripts but something went wrong.
# Please make sure that your network settings allow you to download scripts from the following domain:"""

#     text = """\
# I have had access to the much-rumored OpenAI “Strawberry” enhanced reasoning system for awhile, and now that it is public, I can finally share some thoughts1. It is amazing, still limited, and, perhaps most importantly, a signal of where things are heading.
# The new AI model, called o1-preview (why are the AI companies so bad at names?), lets the AI “think through” a problem before solving it. This lets it address very hard problems that require planning and iteration, like novel math or science questions. In fact, it can now beat human PhD experts in solving extremely hard physics problems.
# To be clear, o1-preview doesn’t do everything better. It is not a better writer than GPT-4o, for example. But for tasks that require planning, the changes are quite large. For example, here is me giving o1-preview the instruction: Figure out how to build a teaching simulator using multiple agents and generative AI, inspired by the paper below and considering the views of teachers and students. write the code and be detailed in your approach. I then pasted in the full text of our paper. The only other prompt I gave was build the full code. You can see what the system produced below.
# But it is hard to evaluate all of this complex output, so perhaps the easiest way to show the gains of Strawberry (and some limitations) is with a game: a crossword puzzle. I took the 8 clues from the upper left corner of a very hard crossword puzzle and translated that into text (because o1-preview can’t see images, yet). Try the puzzle yourself first; I am willing to bet that you find it really challenging.
# Crossword puzzles are especially hard for LLMs because they require iterative solving: trying and rejecting many answers that all affect each other. This is something LLMs can’t do, since they can only add a token/word at a time to their answer. When I give the prompt to Claude, for example, it first comes up with an answer for 1 down (it guesses STAR, which is wrong) and then is stuck trying to figure out the rest of the puzzle with that answer, ultimately failing to even come close. Without a planning process, it has to just charge ahead.
# But what happens when I give this to Strawberry? The AI “thinks” about the problem first, for a full 108 seconds (most problems are solved in much shorter times). You can see its thoughts, a sample of which are below (there was a lot more I did not include), and which are super illuminating - it is worth a moment to read some of it.
# The LLM iterates repeatedly, creating and rejecting ideas. The results are pretty impressive, and it does well… but o1-preview is still seemingly based on GPT-4o, and it is a little too literal to solve this rather unfair puzzle. The answer to 1 down “Galaxy cluster” is not a reference to real galaxies, but rather a reference to the Samsung Galaxy phone (this stumped me, too) - “APPS.” Stuck on real galaxies, the AI instead kept trying out the name of actual galactic clusters before deciding 1 down is COMA (which is a real galactic cluster - I had no idea). Thus, the rest of the results are not correct and do not fit the rules exactly, but are pretty creative: 1 across is CONS, 12 across is OUCH, 15 across is MUSICIANS, etc.
# To see if we could get further, I decided to give it a clue: “1 down is APPS.” The AI takes another minute. Again, in a sample of its thinking (on the left) you can see how it iterates ideas.
# The final answer here is completely correct, solving all the hard references, though it does hallucinate a new clue, 23 across, which is not in the puzzle I gave it.
# So o1-preview does things that would have been impossible without Strawberry, but it still isn’t flawless: errors and hallucinations still happen, and it is still limited by the “intelligence” of GPT-4o as the underlying model. Since getting the new model, I haven’t stopped using Claude to critique my posts - Claude is still better at style - but I did stop using it for anything involving complex planning or problem solving. It represents a huge leap in those areas.
# Using o1-preview means confronting a paradigm change in AI. Planning is a form of agency, where the AI arrives at conclusions about how to solve a problem on its own, without our help. You can see from the video above that the AI does so much thinking and heavy lifting, churning out complete results, that my role as a human partner feels diminished. It just does its thing and hands me an answer. Sure, I can sift through its pages of reasoning to spot mistakes, but I no longer feel as connected to the AI output, or that I am playing as large a role in shaping where the solution is going. This isn’t necessarily bad, but it is different.
# As these systems level up and inch towards true autonomous agents, we're going to need to figure out how to stay in the loop - both to catch errors and to keep our fingers on the pulse of the problems we're trying to crack. o1-preview is pulling back the curtain on AI capabilities we might not have seen coming, even with its current limitations. This leaves us with a crucial question: How do we evolve our collaboration with AI as it evolves? That is a problem that o1-preview can not yet solve.
# The usual reminder - I am not paid or compensated in any way by any AI company. OpenAI was not shown this piece before I published it (nor did they ask). I did not know when the model was going to be released in advance.
# Substack is the home for great culture"""

#     text = """\
# Payers save millions and improve the member experience
# A member’s coverage situation can change numerous times throughout their lives or even in a single year, making it challenging for payers to identify accurate and complete coverage information to determine the primary payer. Having complete coverage information is critical for payment integrity, optimal operational efficiencies, and effective cost containment. Without it, payers must invest in time-consuming research and manual management of coverage-related appeals, as well as higher call center volumes and increased provider friction. Also, payers may unnecessarily struggle to meet employer contractual commitments.
# In addition to ongoing staffing challenges and skyrocketing expenses, payment integrity issues increase a payer’s financial risk and negatively impact the member experience.
# Payers now have a more effective way to identify complete, accurate coverage information to determine the primary payer. Avaneer Coverage Direct™ gives payers a direct connection to all providers and all other payers on the Avaneer Network™, simplifying and improving the sharing of primary, secondary, and tertiary insurance information without aggregating the data or sending it to third parties outside the network. Data remains safely within the network and under the complete control of the data originators.
# When a change is made to a member’s coverage, Avaneer Coverage Direct identifies missing, conflicting, incorrect information, and new coverage availability, instantly “pushing” this insight update to all network participants providing services to the member. Immediately sending updated information to all permissioned payers and providers ensures providers have correct coverage information at the point of care and payers will have fewer first-pass denials to manage. Sharing new and complete coverage information also delivers increased Coordination of Benefits (COB) leads, improves insurance primacy validation, and lowers provider calls. The result is reduced administrative burden, significant cost savings, and improved member satisfaction.
# Avaneer Coverage Direct is just one of the solutions available on the Avaneer Network, a digital network and platform that simplifies the business of healthcare. Designed as a modern IT infrastructure for sharing healthcare data, Avaneer Health enables payers to work with their providers more easily, which ultimately benefits the member.
# Each payer and provider participating in the Avaneer Network receives their own provisioned cloud environment, known as a SparkZone™. Once a participant loads coverage information for their members/patients into their SparkZone, the Avaneer Coverage Direct process begins:
# Avaneer Coverage Direct launched with two large national payers and a nonprofit, multi-specialty health system with nearly 80,000 employees worldwide. Like many payers, establishing the primary payer is vital for controlling costs and improving payment accuracy. However, the payers’ and provider’s available data is siloed and latent, and current methods for discovering dually-covered members are challenging and limiting. Despite their best efforts, current technology and manual processes don’t provide complete coverage information. Even when the data is found, the information may be incorrect, conflict with other coverage information, or it is not comprehensive and does not represent the individual’s full benefit picture. Bad coverage data leads to denied claims, write-offs, delayed reimbursement, and lost revenue.
# The first of its kind, Avaneer Coverage Direct connects the payers and the provider directly. With this single connection to the Avaneer Network, payers and providers can share real-time, current, minimally necessary granular data with those having permissioned access. Data is never centralized or aggregated, allowing each payer and provider to retain control of their data using their encryption keys.
# With Avaneer Coverage Direct, the payer experienced short-term hard savings of between $0.57 to $1.65 per claim.
# The payer also experienced an increase in payment integrity, issue resolution, and coverage primacy. With a reduction in manual workflows, the payer can reassign staff to more strategic tasks.
# It’s time to move past outdated, labor-intensive administrative processes that increase friction, reduce member satisfaction, and cost payers billions. Avaneer Coverage Direct makes it possible.
# Learn how your organization can benefit from Avaneer Coverage Direct.
# Our monthly newsletter gives the latest news on interoperability, automation, digital transformation, and other important trends. There's a lot happening and every month we keep healthcare leaders and innovators informed.
# A member’s coverage situation can change numerous times throughout their lives or even in a single year, making it challenging for payers to identify accurate and complete coverage information to determine the primary payer. Having complete coverage information is critical for payment integrity, optimal operational efficiencies, and effective cost containment. Without it, payers must invest […]
# The Nashville General Hospital leadership team has embarked on an inspiring transformation journey, challenging what it means to serve its community.
# The Nashville General Hospital leadership team has embarked on an inspiring transformation journey, challenging what it means to serve its community.
# Fill out the form and we will contact you to schedule a tour of the Avaneer Network™
# During the tour you will learn:
# Request a product tour today and learn how Avaneer Health can help your organization achieve complete data fluidity through a single connection to the Avaneer Network.
# Join us as we reinvent the business of healthcare!
# Where healthcare leaders come together to share data and create solutions – to deliver the greatest possible care.
# We use cookies to give you the best online experience. By agreeing you accept the use of cookies in accordance with our cookie policy.
# When you visit any web site, it may store or retrieve information on your browser, mostly in the form of cookies. Control your personal Cookie Services here.
# """

#     text = """\
# Health system CIOs and CFOs are accountable for driving forward the CEO's vision and powering strategic priorities. The most effective duos have learned to speak each others' language and respect their partner's expertise.
# But a looming issue will pose a challenge for them in the coming months. At the Becker's Health IT + Digital Health + Revenue Cycle Conference in Chicago in early October, a panel of CIOs warned an audience of their peers about the most important areas to watch.
# Mike Restuccia, CIO of Penn Medicine in Philadelphia, said introducing new, innovative technologies will be a big challenge in the next few years as expenses move from capital to operational.
# "We're not sure of what the price point is or the cost point will be," he said. "I particularly look at the cloud and everyone says it's so much less expensive to go to the cloud and there is a breakpoint where it is less expensive, but then it's more expensive. I don't think CFOs totally understand where that break point is. I don't yet, and it's changing every day because new technology gets introduced and price points go down, or price points go up."
# The price point is a moving target and can have negative consequences if leaders don't realize how much the costs are adding up.
# "That's going to be a point of contention moving to the cloud," said Mr. Rustuccia.
# Nader Mherabi, executive vice president and chief digital and information officer at NYU Langone Health in New York City, agreed. He noted CFOs are sensitive to liquidity as days cash on hand eroded over the last few years, affecting the institution's credit ratings.
# "You have to really work collaboratively with the CFO to do projections. The toughest part of our role is to say to the CFO what percentage of your budget is going to shift from CapEx to OpEx and what does that translate to in value of dollars," said Mr. Mherabi. "Because not one-to-one OpEx to CapEx, you can't negotiate that way. There's a lot of smart CFOs and they figure out that that's not balanced."
# Hospital margins have improved since last year, but growth is slow and has remained relatively flat at 4.2% since May, according to Kaufman Hall.
# "That's going to continue to get contentious given that healthcare margins are so anemic in every market," said Mr. Mherabi.
# Daniel Barchi, senior vice president and CIO of Chicago-based CommonSpirit Health, agreed the capital versus operating expenses conversation will challenge CIO and CFO relationships in the near future.
# "For all of us to say the exact same thing should be an eye-opener for everyone, whether it's the cloud or software-as-a-service, or endpoint, and thick client versus thin client," he said. "We've got 225,000 devices and when they go from thick to thin, we're putting it out in the internet of things, and in the cloud, and supporting them as a service. OpEx just starts to add up."
# Mr. Barchi said it's critical for health system leaders to keep these expenses in the forefront for long-term planning.
# "The cliff is coming very quickly for when OpEx is the critical element in our budget, and then from a vendor point of view, you need to be thinking about how you make it possible to ingest this and either offset costs or make it capitalizable in a way that for all of us to say: 'Oh, it's capital. Yeah it's easy.' or 'It's OpEx, I'm sorry, I can't even talk to you'," said Mr. Barchi. "That's fundamentally where we are right now."
# One more sticking point for CIOs and CFOs could be cybersecurity. Hospitals and health systems understand the gravity of ransomware attacks and they're spending big in key areas to fortify their defenses, and then have a plan for when a breach occurs.
# "Aside from practicing tabletop with leadership on ransomware, we also practice once or twice per year with our finance departments to see what happens," said Mr. Mherabi. "If something major is happening, that might not even be a ransomware attack, it could be just a major outage affecting supply chain or payroll, which are finance-dependent. What do we do? What are the steps we practice? How do we pay people? How do we secure the supply chain."
# The exercise helps the CFO appreciate that the CIO is paying attention to the finance leadership's responsibilities and not focused just on the IT perspective.
# Copyright &copy 2024 Becker's Healthcare. All Rights Reserved. Privacy Policy. Cookie Policy. Linking and Reprinting Policy.
# Copyright © 2024 Becker's Healthcare. All Rights Reserved. Privacy Policy. Cookie Policy. Linking and Reprinting Policy. | Employee Access
# The Becker's Hospital Review website uses cookies to display relevant ads and to enhance your browsing experience. By continuing to use our site, you acknowledge that you have read, that you understand, and that you accept our Cookie Policy and our Privacy Policy.
# """

#     text = """\
# Healthcare innovation takes the stage in Las Vegas next week with HLTH, but attendees heading to Sin City for the latest in health and wellness may be looking for something a bit more inclusive than in years past.
# As the industry transitions, albeit slowly, to patient-centered care and embraces ideas like AI and virtual care, healthcare leaders are looking for comprehensive solutions, rather than new tools and programs that target certain conditions or populations.
# It’s part of what Meghan Cassidy, senior director of sales and product development for market and network services at Cleveland Clinic, calls “point solution mania.”
# “I understand why the industry started there, but now it seems there are hundreds of those types of solutions in the market,” she says. “So I am hopeful that this year [people] will come to try to figure out how to weave all of those solutions together.”
# “They all have great ROI, they all have great patient outcomes, but they're ultra-segmented right now,” she adds.
# Healthcare has long had this issue, and events with large exhibit halls are ideal places to view the expanse of vendors driving innovation. But the industry is in a tough place right now, struggling to address cost and quality issues and workforce shortages, and it needs programs and tools that can be applied across the enterprise, not bolting onto platforms but integrating with them—what Cassidy calls “the quilt that ties it together.”
# HLTH is somewhat unique in that it attracts healthcare organizations and companies that are interested in whole patient care, rather than healthcare information technology or clinical care. So the reasons and the opportunities for integration are more apparent. And that’s why topics like food as medicine, women’s health, mental health, psychedelics and art and music treatments have a place in the exhibit hall and in sessions.
# That’s also what draws a unique cross-section of the healthcare industry to Sin City. Cassidy, for example, is focused on programs and tools that would help Cleveland Clinic deliver healthcare services to employers. It’s an evolving field that hospitals and health systems are exploring, and one that the so-called disruptors like Amazon and Google have been targeting.
# “They're not offering an app for something anymore,” she points out. “They're going in and saying, ‘Let's share risk with these primary care facilities or primary care companies and try to change the care and get more people into their primary care doctor up front. And that will of course lead to cost savings later on down the line.”
# With primary care as the focal point of healthcare access, many tools and programs are aimed at reducing barriers to access and facilitating a seamless primary care visit, whether it be in person or virtual. But true innovators in this space are also expanding the definition of primary care to include more preventive health and wellness opportunities, with the idea that a consumer/patient and care provider are on a journey together.
# HLTH gives healthcare executives an opportunity to expand that conversation, looking at different ways, both strategic and technological, to configure care management and coordination. And it wouldn’t be a healthcare conference if AI weren’t included in that discussion.
# But HLTH also tends to draw the big names and organizations, offering solutions that those hospitals and health systems can afford to try out. Cassidy says she’d like to see more tools and strategies for smaller and more rural organizations.
# “There's a lot of marquee names that are out there that are saying what they do, but they represent very large companies and have large pockets,” she says. “With the small employers who are struggling, like the mom and pop shops on the corner, thinking about more ways to intervene and help them would be very, very interesting and effective.”
# And while this event in particular carries the glitz and glamor that Las Vegas attracts, there are a few more celebrities than in past years—evidence, perhaps, of the energy brought to bear on issues like maternal health, mental health and chronic conditions. First Lady Jill Biden will talk about women’s health research during a Main Stage session on Wednesday, while entertainers John Legend, Halle Berry, Maria Shriver, Lennie Kravitz and Lance Bass are scheduled to appear as well.
# Regardless of the star power, HLTH offers healthcare leaders an intriguing look at how the industry is evolving beyond episodic care, and how new ideas and technologies can shape their organizations to deliver what patients not only need by want.
# Eric Wicklund is the associate content manager and senior editor for Innovation at HealthLeaders.
# The annual HLTH conference sits at the junction of innovation and health and wellness, giving attendees a look at how the patient care journey is evolving.
# Healthcare leaders attending the event are looking beyond point solutions that address specific conditions or populations, and are focused more on technology and strategies than can be integrated across the enterprise.
# integrated care
# Physicians are in short supply. They are costly. Is the APP the answer to the CMO's workforce and budget challenges? ...
# Amid the hype and promise, a growing tension is becoming clear: the reality of what AI can deliver versus what it can't. ...
# """

    url = "https://www.roadandtrack.com/news/a63081162/volkswagen-rivian-mk9-golf/"
    title = "Volkswagen Says Rivian Will Help Develop Electric Mk9 Golf"
    text = """\
American software will meet Volkswagen hardware in the next-generation version of the iconic hatchback.
Volkswagen and Rivian are joining forces as part of a $5.8 billion dollar deal, one that will see the two companies co-develop architectures and software for future electric vehicles. Now, one VW exec has confirmed where we'll first see the fruits of this joint development between the legacy German automaker and the U.S. startup: the next-generation Volkswagen Golf.
According to reporting from CarSales, development of the electrified hatchback is set to start soon, and Volkswagen is seemingly excited to leverage the engineering prowess and zonal architecture of Illinois's premier electric pickup truck manufacturer. Currently in its eighth generation, the Volkswagen Golf just received a facelift for the 2025 model year, meaning the ninth-generation version of this iconic compact isn't set to arrive until 2029.
Even so, Thomas Schaefer, Volkswagen’s passenger cars chief executive, confirmed earlier this week that the joint partnership between Rivian and Wolfsburg will be used first on the hatchback whose roots date back to the 1970s.
"We decided on how to do the software-defined vehicle. It will happen with Rivian, the joint venture, where we put the new electric electronics architecture together," Schafer said to the media. "But we have also decided that we want to start this journey with a more iconic product. So, we’ll start with the Golf."
Details remain sparse, but reports from CarSales indicate that the same shared electronic package will eventually make its way into Audi and Porsche products as well. Before that crossover, however, Volkswagen will first test the Rivian-designed software on its Scalable System Platform (SSP). Currently in development, the SSP will replace the MEB platform, which currently holds the ID-series of electric VWs. Notably, CarSales says the MK9 Golf Electric will replace the current ID.3 as VW's compact electric model.
Rivian leadership has previously spoken out against the use of 800- and 900-volt architecture, indicating that this compact hatch may be a lower-voltage build. However, as consumers have voiced complaints about slower charging speeds on current ID-series models, we wouldn't be surprised to see VW push for the more powerful setup.
Volkswagen previously offered the original E-Golf in the U.S. from 2015 through 2020 before culling the electrified Mk7 chassis. It's not immediately clear which markets the Mk9 Golf will be available in, seeing as the North American market has been void of a traditional Golf offering since 2021. We've retained the performance-forward GTI and Golf R, but the reintroduction of the Golf as an electric model for 2029 would be a big deal for the U.S. market.
A New York transplant hailing from the Pacific Northwest, Emmet White has a passion for anything that goes: cars, bicycles, planes, and motorcycles. After learning to ride at 17, Emmet worked in the motorcycle industry before joining Autoweek in 2022 and Road & Track in 2024. The woes of alternate side parking have kept his fleet moderate, with a 2014 Volkswagen Jetta GLI and a BMW 318i E30 street parked in his Queens community.
"""

    print(json.dumps(summarize_text(url, title, text), indent=2))

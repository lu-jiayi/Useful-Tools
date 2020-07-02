
import csv
import warnings
import pytest
import pandas as pd

#Part 1 of this project requires the csv file ("input.csv") in the directory;
#part 2 of this project requires the txt file ("results.txt") in the directory;

######################################################################################################
######################################################################################################
                                                ###Part 1###
                                            #This part reads input from a csv file containing 
                                            #all test/filler sentence for an online acceptability judgment
                                            # experimtn with item and condition information,
                                            #and convert it to a javascript txt file that IbexFarm can read



#This function reads-in a csv file with three columns: condition, item, context, and target; All test condition name start with the same letter "t" (for "test"), 
# and filler condition name start with letter "f" for "filler" 
#This function outputs a list of dicts, with each dict having four (or three) entries: condition(str), item(int), context(str), and target(str)

def context_csv_to_dict(filename: str, context:bool = True) -> list:
    output_list = []
    with open(filename, newline='', encoding="utf-8-sig") as csvfile:
        reader =csv.DictReader(csvfile, delimiter = ",")
        for rows in reader:
            if (len(rows) != 4 and context) or (len(rows) != 3 and not context):
                warnings.warn("Wrong number of columns in input csv")
            output_list.append(dict(rows))
    return output_list


#This function takes in a list containing the following information: 
#{"condition": name (str), "item": item number (int), "context": context paragraph(str, optional), "target": test sentence(str)]
# and turns it into the javascript format that IbexFarm can read. Context is optionally included only when 
#context == True, and display width is set to 40 by default. 


def item_to_script_converter(input_dict: dict, context:bool = True, width:int = 40) -> str:
    if not isinstance(input_dict, dict):
        raise TypeError("item_to_script_converter exptects type dict")
    if (not context) and (not len(input_dict) == 3):
        warnings.warn("Excess entries in input_dict")
    cond = str(input_dict["condition"])
    item_num = str(input_dict["item"])
    if context:
        context_str = str(input_dict["context"])
    test_sentence = str(input_dict["target"])
    format_str_head = f"""[["{cond}",{item_num}], q,{{s: {{html: "<div style='width: {width}em;'>"""  
    format_str_end = f"""<b>Target:</b>{test_sentence}</div>"}}}}],\n"""
    if context:
        format_str_context=f""" <b>Context:</b>{context_str}</div><div style='width: 40em;'><p></p>"""
    else:
        format_str_context=""
    whole_script = format_str_head + format_str_context + format_str_end
    return whole_script

@pytest.mark.parametrize("example, context, expected", [
        [{"condition":"filler_d","item":93, "context":"this is context paragraph", "target": "this is test sentence"}, True, """[["filler_d",93], q,{s: {html: "<div style='width: 40em;'> <b>Context:</b>this is context paragraph</div><div style='width: 40em;'><p></p><b>Target:</b>this is test sentence</div>"}}],\n"""],
        [{"condition":"cond_a", "item":12, "context":"this is context!", "target":"this is test sentence!"}, True, """[["cond_a",12], q,{s: {html: "<div style='width: 40em;'> <b>Context:</b>this is context!</div><div style='width: 40em;'><p></p><b>Target:</b>this is test sentence!</div>"}}],\n"""],
        [{"condition":"cond_a", "item":12, "target":"this is test sentence!"}, False, """[["cond_a",12], q,{s: {html: "<div style='width: 40em;'><b>Target:</b>this is test sentence!</div>"}}],\n"""]
        ]
)
def test_item_to_script_converter(example, context, expected):
    result = item_to_script_converter(example, context=context)
    assert result == expected


#This function loops over the output list of dicts from context_csv_to_dict, and apply item_to_script_converter
def loop_over_all_items(filename:str, context:bool = True, width:int = 40) -> str:
    print("Converting input format...")
    output_str = ""
    item_list = context_csv_to_dict(filename, context)
    for i in item_list:
        output_str += item_to_script_converter(i, context, width)
    #delete last two characters: comma and linebreak from the last item:
    output_str = output_str[:-2]
    return output_str

#Add consent and practice; 
# Assuming test condition names start with the letter "t", and filler conditions start with letter "f".
def add_consent_and_practice(filename, test_cond = "t", filler_cond = "f", context = True, width = 40):
    consent_practice_java = f"""var shuffleSequence = seq("consent", "setcounter", "intro", "prepractice", "practice", "getReady", sepWith("sep", rshuffle(startsWith("{test_cond}"),startsWith("{filler_cond}"))),"exit");

var showProgressBar = true
var practiceItemTypes = ["practice"];

var counterOverride = 2;

// Just to avoid typing AcceptabilityJudgment over and over.
var q = "AcceptabilityJudgment"
var defaults = [
    Separator, {{ transfer: 500, normalMessage: "Please wait one moment." }},
    AcceptabilityJudgment, {{as: ["1", "2", "3", "4", "5", "6", "7"], presentAsScale: true, instructions: "Use a number key or click on a box.", leftComment: "(Very unnatural)", rightComment: "(Very natural)" }}
];

var items = [

// Increment counter
//["setcounter", "__SetCounter__", {{ }}],

["sep", Separator, {{ }}],

["consent", "Form", {{consentRequired: true, html: {{include: "workerID_test.html"}}}}],

["consent", "Form", {{consentRequired: true, html: {{include: "consent.html" }}}} ],

["consent", "SSForm", {{consentRequired: true, html: {{include: "intro.html" }}}} ],

["iriTest", "Form", {{consentRequired: true, html: {{include: "IRI_survey.html"}}}}],

["exit", "Form", {{consentRequired: false, html: {{include: "debrief.html" }}}} ],

["exit", "Form", {{consentRequired: false, html: {{include: "exit.html" }}}} ],


["intro", "Message", {{consentRequired: false,
                    html: ["div",
                            ["p", "Welcome.  In this experiment, you'll be reading some English sentences: one context paragraph, and one target sentence. For the sentences you see, please give your rating of whether the TARGET SENTENCE of each pair seems like a natural English sentence or not. If it sounds natural, give it a high rating (6 or 7). If you think that the sentence does not sound like a natural sentence of English, then you should give it a low rating (1 or 2). You do NOT need to rate the context paragraphs."],
                            ["p", "You should judge the target sentences not according to school grammar, but instead according to your intuitions about what counts as natural English. For example, 'school' grammar tells us that we should not end sentences with a preposition. However in modern English, a sentence with a preposition at the end such as 'That's the man I'm talking about' is perfectly natural. You might rate that sentence a 5 or a 6."]
                          ]}}],

["prepractice", "Message", {{consentRequired: false,
                    html: ["div",
                            ["p", "Note that in this questionnaire you are NOT being asked to judge the plausibility of the meaning of the sentence; you are simply being asked to judge whether the target sentence sounds natural or not. The target sentence below describes an unlikely situation, although it has the form of a very natural English sentence. Given the proper circumstances (maybe in a fairy tale), this could be a very reasonable sentence, and so you might want to rate it a 6 or a 7."],
                            ["p", "Context: John wanted to know what Eric saw."],
                            ["p", "Target: He said that the purple elephants are climbing up the trees."]
                          ]}}],

["prepractice", "Message", {{consentRequired: false,
                    html: ["div",
                            ["p", "Remember, you're being asked to judge the naturalness of the target sentences. However, sometimes the sentences we use can be quite long and complicated, and still remain natural. Here's an example of a long, complicated sentence that is nonetheless natural. You might rate it a 4 or a 5."],
                            ["p", "The president was asked who the CIA thought the nation was at risk from when he appeared at a press conference on TV."]
                          ]}}],

["prepractice", "Message", {{consentRequired: false,
                    html: ["div",
                            ["p", "Likewise, short sentences can be completely unnatural, even if you understand what the sentence might mean. Here's an example of a short and simple sentence that is highly unnatural. You might rate it a 1 or a 2."],
                            ["p", "The cats the trees climbed."]
                          ]}}],

["prepractice", "Message", {{consentRequired: false,
                    html: ["div",
                            ["p", "Remember that each sentence is different, and you may very well feel differently towards two sentences which might seem superficially similar, so it is important that you judge each sentence on its own merits and not compare it to other sentences that you may have read."],
                            ["p", "It is very important to read the context sentence *before* reading the target sentence!"],
                            ["p", "Lastly, there will be a lot of variation in the sentences you read, and they won't all neatly fall into 'good' and 'bad' cases. So try to use the entire 1-7 rating scale, and give careful consideration to how natural each sentence sounds to you!"],
                            ["p", "Let's try some practice."]
                          ]}}],
                          
["practice", q, {{s: ["div", ["p", "Context: It was Christmas time, and everyone was really excited."],
                ["p", "Target: The kids decorated the ornaments onto the tree."]]}}],
["practice", q, {{s: ["div", ["p", "Context: John asked me yesterday who all was going to be coming over."], 
                ["p", "Target: I know that Bill and Mary were planning on attending the party last night."]]}}],
["practice", q, {{s: ["div", ["p", "Context: Mary is usually fairly skeptical of public officials."], 
                ["p", "Target: Which politician did she believe the scientist and?"]]}}],
["practice", q, {{s: ["div", ["p", "Context: Unfortunately, Susy was a little bit out of the social loop."], 
                ["p", "Target: John doubted that she knew anything of what went on after work."]]}}],

["getReady", "Message", {{consentRequired: false,
                        html:  ["div",
                            ["p", "That's it for the practice. Here's a quick reminder of what to do:"],
                            ["p", " (1) Read each context/target pair carefully so that you understand what it means."],
                            ["p", " (2) Rate the naturalness of the target sentence only."],
                            ["p", " (3) Use your gut intuitions, not school grammar!"],
                            ["p", "Click below when you're ready to begin."]
                          ]}}], \n"""

    consent_practice_java += loop_over_all_items(filename, context, width)
    return consent_practice_java
#This function is the main function to call upon: it writes the output of add_cosent_and_practice to a txt file, which can 
#be uploaded to IbexFarm. 
def write_txt(filename, context = True, width = 40):
    f = open("ibex_format.txt", "w")
    f.write(add_consent_and_practice(filename, context, width))
    f.close()
    print("Input file converted to javascript for IbexFarm. File saved as 'ibex_format'.txt")

######################################################################################################
######################################################################################################
                                                ###Part 2###
                                        #This part reads the result csv file from IbexFarm
                                        #and clean out irrelevant information other than 
                                        #response and response time for each token, and write it 
                                        #to a new csv file for future analysis use. 

#This function opens the result txt file,clean away irrelevant contents, 
# and turns it into a dataframe with columns: subject, item, condition, response, response_time
def clean_result_txt(filename:str):
    whole_result = []
    with open(filename, newline='', encoding="utf-8-sig") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 11:
                if row[2] =="AcceptabilityJudgment":
                    token_list = []
                    #subject name
                    token_list.append(str(row[0]))
                    #item
                    token_list.append(row[3])
                    #condition
                    token_list.append(row[5])
                    #response
                    token_list.append(row[8])
                    #response time
                    token_list.append(row[10])
                whole_result.append(token_list)
    output_df = pd.DataFrame(whole_result, columns = ["subject", "item", "condition", "response", "response_time"])
    return output_df

#This function deletes all tokens with response time higher and lower than certain thresholds. 
# Default upper bound is 100000 ms (100s), and default lower bound is 3000ms (3s). 
def clean_extreme_response_time(filename, upper=100000, lower = 3000):
    df = clean_result_txt(filename)
    df["response_time"] = pd.to_numeric(df["response_time"])
    clean_df = df[(df.response_time > lower) & (df.response_time < upper)]
    return clean_df

#This is the main function to call upon in part 2. It writes the output of clean_extreme_response_time to a csv 
#named "result_clean.csv". 
def write_result(filename: str, interpolate_extreme: bool = True):
    if not interpolate_extreme:
        df = clean_result_txt(filename)
        print("Tokens with extreme response times are NOT removed.")
    else:
        df = clean_extreme_response_time(filename)
        print("Tokens with extreme response times are removed.")
    df.to_csv("result_clean.csv", encoding='utf-8')
    print("Clean result saved as `result_clean.csv'.")


if __name__ == '__main__':
#running part 1: this requires the input.csv file in the directory.
   write_txt("input.csv", context = True, width = 40)
#running part 2: this requires the results.txt file in the directory. 
   write_result("results.txt")
   


        

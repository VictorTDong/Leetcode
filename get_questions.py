import json
import os
import requests

#Categories
TOP_100 = 'top-100-liked-questions'
TOP_INTERVIEW = 'top-interview-questions'

LIST_ID = TOP_100

# Get the list of problems
data = {
    "operationName": "problemsetQuestionList",
    "variables": {"categorySlug":"","filters":{"listId":LIST_ID},"limit":1000},
    "query": "\n query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {\n problemsetQuestionList: questionList(\n categorySlug: $categorySlug\n limit: $limit\n skip: $skip\n filters: $filters\n ) {\n total: totalNum\n questions: data {\n acRate\n difficulty\n freqBar\n frontendQuestionId: questionFrontendId\n isFavor\n paidOnly: isPaidOnly\n status\n title\n titleSlug\n topicTags {\n name\n id\n slug\n }\n hasSolution\n hasVideoSolution\n }\n }\n}\n "
}

resp = requests.post('https://leetcode.com/graphql', json=data)

problems = [{'titleSlug' : problem["titleSlug"], 'acRate' : problem["acRate"], 'frontendQuestionId' : problem["frontendQuestionId"]} for problem in resp.json().get('data').get('problemsetQuestionList').get('questions')]
problems.sort(key=lambda x: x["acRate"], reverse=True)

with open(LIST_ID + '.json', 'w', encoding='utf-8') as f:
    json.dump(problems, f, ensure_ascii=False, indent=4)
    
# Get data for each problem
for question in problems:
    data = {
        "operationName": "questionData",
        "variables": {"titleSlug": question["titleSlug"]},
        "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    title\n    titleSlug\n    content\n    difficulty\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    exampleTestcases\n    metaData\n  }\n}\n"
    }
    
    resp = requests.post('https://leetcode.com/graphql', json=data)
    
    problem = resp.json().get('data').get('question')
    
    path = LIST_ID + '/' + problem["questionId"] + '. ' + problem["title"]
    if not os.path.exists(path):
        os.makedirs(path)    
        
        for i in range(len(problem['codeSnippets'])):
            if problem['codeSnippets'][i]['lang'] == 'C++':
                with open(path + '/' + problem["titleSlug"] + '.cpp', 'w', encoding='utf-8') as f:
                    f.write(problem['codeSnippets'][i]['code'])
                break               
            
        with open(path + '/' + problem["title"] + '.txt', 'w', encoding='utf-8') as f:
            f.write("Title: " + problem['title'] + "\nQuestion ID: " + problem['questionId'] + "\nAcceptance rate: " + str(question['acRate']) + "\nTestcases:\n" + problem['exampleTestcases'] + "\n") 
            
        with open(path + '/' + problem["titleSlug"] + '.html', 'w', encoding='utf-8') as f:
            f.write(problem['content']) 

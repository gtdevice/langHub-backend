Improve user flow:
User opens articles list:
* GET /discover - user gets the list of possible articles
* POST /generate - user can ask for generation of new articles

How relation between tables could look like for a1 - article (u1, u2 and u3 - users)
-------------------------------------
Article - adopted_article - user_article
a1          a1 - language1          u1 - a1 - language1
            a1 - language2          u2 - a1 - language2
                                    u3 - a1 - language1
---------------------------------------            

Plan for work
Step 1)
We need to keep track of user's articles
POST /generate:
we need to add new table user_x_adopted_article - in order to keep track of users specific list of articles
check:
    if there are more adopted_articles (select adopted_article where ... and id>last user_article.article_id order by ID desc limit 3) and add to the user_x_adopted_article
        if not - check if there are articles (select article where ... and id>last adopted_article.article_id order by ID desc limit 3) and adopt them and add to the user_x_adopted_article
            if not - generate article, adopt them and add to the  user_x_adopted_article

GET /discover must show articles that only are in user_x_adopted_article


Step 2) we need to create the separate endpoint
POST /freeText
this endpoint will send the users text to the LLM for analysys, save the result of the anlysis along with the text and return to the user results of the analysis
The data structure [id, user_id, text, metadata] - in the metadata will be result of the analysis
Step 3) separate endpoint POST /learnbook
input: multipart data: bin - photo of the task from the book, json - text - the user's answer to the task
from the book. The process if splitted: 1) send photo to the LLM and recognize the task - get the text description from the photo of what should be done. 
save the data [task - description that we have got from LLM; answer - users answer; metadata - None]. After that we send another request to the LLM and ask to review users answer against the task.
as the result we get the metadata, that will be saved to the existing entry, and everything will be returned to the user. (we will not save nor return photo. we return only text).
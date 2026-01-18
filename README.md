# IMPORTANT INFORMATION: ARC @ UCF DOCUMENTATION

**Relevant documentation available after Preamble and Personal Message**

**Skip to [Project Goal/Guidelines](#project-goalguidelines) to begin reading documentation. Read Preamble and Personal Message for other information.**

## Preamble

This is the README file for ARC ALERTS @ UCF. 

The file "documents" contains documentation information for each year.

As you read through the documents in the documents file, each document will likely carry a date, unless it isn't date specific. The format is in DD-MM-YYYY. Times might be listed in various formats. 24-hour might be standard, especially for documents written by me. 

API information, discussions, product ideas, improvements, etc. will be documented in here and discussed. Release information on the GitHub repo will also contain relevant information. These documents will provide an insight into reasonings and whys.

A lot of this project is based around several different principles: programming, psychology, meteorology, and public safety. 

Pyschology and Public Safety go hand-in-hand. Meteorology is an important concept while working with this code. And programming is a necessary.

You will definitely learn how the NWS formats alerts, what information alerts have, how to handle APIs, and how to aggregate this information and disseminate this information effectively.

At all times, I will maintain that improvements should be and can be made. But they should be discussed. 

Will talk no further, ref later portions.

ZCZC

## Personal Message

The documents folder should, if it exists when I leave, carry with it documentation written up by people for this project. These proposals/discussions are, in my mind, extremely important. 
In industry, you're going to need to make proposals and deliver them to someone else, especially to get projects off the ground. I value providing real-world experience, and even though I'm writing this as a freshman, I do think I have valuable information worth sharing. 

I encourage you to do exactly what I've done and what maybe predecessors have done: create documentation, detail ideas, detail what's confirmed and implemented, what you're working on implementing, what you want to discuss, maybe you even want to add it but want to discuss the implementation of it. Do it, even if it takes a bit of effort. Maybe you don't have to pour your heart and soul out into it, but still do it. Make it small, make it large, whatever you want to do and feel like doing. I just ask you do something. 

Documentation is extremely important, and it can help carry forward the original vision and intent of projects. And some of that vision I intend to share here with you. 

When you code, make comments. Describe what you're doing and why you're doing it like you're teaching someone. Talk to someone while you code. Code together. Review code. Make code better. All of that is part of the process of being on a team. I would know, I live with industry professionals who do code for a living, and I've heard lots of stories, especially of young undergraduates without the soft skills team projects need. 

I might sound like a professor or some other guy telling you what to do, but consider I'm writing this as a freshman. I imagine people who read this might think I'm silly, which, fair. But I do have experience with leadership and management. I've spearheaeded teams and worked on teams, I've worked with people who have no clue how to code. I have, like I said, industry professionals in my same household. I might be young, sure, but I think I have valuable stuff to share. 

Though I am a sensitive person if you get to know me, I'm better at handling my emotions than when I was a kid. I used to take criticism incredibly terribly actually, which was funny. Now I don't. You learn and grow. I guess, make sure you understand people will critique you. Always be open to the fact that someone else might know more about something than you do. Be willing to learn from someone, even from people who are younger than you. They might have a hyperfixation you don't, lol. 

And, understand, you probably will have miscommunications and misunderstandings. Part of why I'm writing this big thing. Part of why I encourage documentation. And why you should prioritize understandable code over fancy code. You make clear what the purpose of something is, people will understand to keep it. 

Idk, you're in the ARC @ UCF club. Learn, grow, make mistakes, screw up, have fun. None of this is serious, none of this is worth a grade. Learn. Break this thing if you have to to learn (just have a backup). But, please, document, document, document. It will help people understand you.

And understand how to work with a team. 

If you ever wanna get in contact with me to discuss any part of this, no matter when and where, you can find me under the username "skyechannelwrx" on Discord, Instagram, Twitter, and GitHub. Contact me on any of those (though GitHub and Discord might be best) and I will answer your questions, but do specify you wanna talk about this project.

Skye[2] signing off.

ZCZC

## Project Goal/Guidelines

The goal of this project is and should always be to provide alert information for all-hazards. This project, aptly named ARC ALERTS @ UCF, is designed to provide alerts for UCF and the wider county area (as listed in the config.py file in utils). 

As you refactor code, rewrite code, or make new code, understand that the ultimate goal of this project is to provide clear, actionable alert information that is easily accessible to any individual. With this in mind, you should follow these guidelines:
 
* Always use visuals where you can, to depict what area is being impacted.
* Be clear and concise, but follow FEMA alerting conventions. FEMA conventions are your ultimate guide here.
* Always talk to your team about removing, adding, or rewriting parts of code.
* Ask questions, always. If you don't understand something, ask. If you must, refer to the `documents` folder and code comments.
* Try to understand the idea behind parts of this project. 
* Do **NOT** take it upon yourself, ever, to remove a feature of the alerting system or systems. Nor for any product information. These provide functionality, especially for severe weather alerts. Further, do not remove portions of these features which include visuals or pertinent information. *Discuss if you want to deprecate a feature*.
* Prioritize functional code over pretty code. Prioritize understandable code over fancy code.
* As general advice: always include documentation. Write comments, especially important ones. **Detail what and why**.
* **You do not have to contribute, but you are encouraged to maintain the `documents` folder. Refer to next section for more information**.

Following these general guidelines will ensure the main functionality of this system is kept. 

## Documentation Information

The `documents` folder contains all relevant documents to this project. These documents, as they are on a public repo, may be heavily redacted for various reasons. Original versions of these documents may be available on the discord. 

Documents, if they are date-specific, will be headed with a `DD-MM-YY` beginning portion of the document name. This is to keep them in order and to log specific dates. 

You are not required to, **but adding to these documents and documentation is encouraged**. Any ideas, discussions, proposals, etc. for this project can be made a document and then placed in the `documents` folder. 

Though this folder is not required, it will contain whys, whats, and hows for different parts of the bot. Explanations for portions of the code may be included in these documents, depending on the version you are working with. These documents are seperated into folders by year.

Ultimately, the purpose of the folder and the documents inside is to preserve feature information, api information, discussion information, and decision information, as well as goals and to ensure that the work is understanable and documented for the future.

Documents produced are intended primarily for internal use to make clear goals and objectives, what needs work, what there might be to implement, pretty much anything as it pertains to the bot. Storing these files in the `documents` folder is *entirely* for reference purposes and to better understand what the bot does. Because documents are initially intended for internal use, information inside of them may need to be redacted before upload to the GitHub repo. Both following sections cover managing existing documents and creating new documents.

**You are asked to not delete `documents` from this project.**

### Managing/Creating Documents

If you are managing these documents or writing a document:

* Create a new year folder for each year.
* The beginning of the file name should include the date of finalization or latest update, in DD-MM-YY format.
* Keep records of current year contributors. If any contributors stop working or leave, you may include the date in which they left.
* Information should include the Committee Chair, the Project Lead(s), and all Contributors. Follow format of previous documents. Include Faculty Advisor always.
* Contributors document is an A5 document. Margins not changed.
* All other documents, if uniformity is wanted (and it is encouraged), should be in B5. Margins not changed.
* Times New Roman Font for main text; change text to a more code-like font for variables, etc. mentioned in the text.
* Use software to redact information as needed before upload or inclusion to project. Make redactions permanent and unrecoverable.
* ***Do not EVER include extremely sensitive information on ANY documentation. This includes, but is not limited to, passwords, birthdays, API tokens, webhook urls, etc.***

Outside of format information included above, you can design the document how you prefer, as long as the necessary information is included.

The following is encouraged:
* A title page.
* A brief summary of changes, or a synopsis of changes. Not detailed.
* A table of contents.
* Page numbers.
* Headers.
* Highlight important information. Someone should be able to read the document, read the highlighted text only, and get an idea of what's going on.
* If able, include diagrams, images, or examples. These are always more effective than words on a virtual paper.

### Redaction Guidelines

Any information which is included in the following should be redacted from the document prior to it being pushed to the GitHub repo. Though the project is to be documented, not all information needs to be or should be shared in these documents. A full, unredacted document should be included internally inside of projects in the ARC @ UCF discord. 

**Your redaction software must permanently redact information and make it unrecoverable. No information redacted should be recoverable from the file.**

**When uploading documents, do not upload the unredacted document. Explicitly label the document as redacted somewhere in the title if any redactions have been made.**

**Alternative to redacting, do not include information you do not want in your document. Or you can rewrite/rephrase your document to obscure, change, or hide identities/information.**

**If any change to the document's available information is made compared to the internal document, you must write in the file name of your document that it's been edited or redacted. You do not need to disclose that the document has been redacted or edited in the document itself.**

Redact the following:
* References/names to/of other club members, unless consent is obtained, including other officers, except for contributors or members of this project.
* References/names to/of contacts outside of the club or outside of UCF, unless consent is obtained to reference them.
* Specific locations, like buildings or addresses. OK to keep general, wider locations, like UCF. Specifics, like UCF Health Sciences 1, **not OK**.
* Meeting locations.
* Discord server-specific info, like invite links, ping roles, specific roles, channels, etc. 
* Personal sensitive information, such as last names, email addresses, social accounts, etc. unless they're a project contributor.
* Comments made by you or another contributor.
* Any references to other clubs, professors, local schools, parks, etc.
* Any information related to the club internally that does not affect the public-face or matter to the documentation.
* The information of votes, except for the outcome.
* Any irrelevant information which, when omitted, does not change the context or meaning of the paragraph or sentence in which it's included, and does not obscure information related to the bot.

Skye[2] personally recommends LibreOffice as an alternative to word. LibreOffice contains redaction features, and features for permanent redaction.

Skye[2] also uses LibreOffice as an alternative to word themselves. 

## Audience

The audience for this project is members of the ARC @ UCF club. However, you may note that you can forward information from the alert channels to other discord servers. If you wish, you may forward such information to other discords as you want. It is encouraged with more extreme alerts. Be aware of specific discord rules when you forward these alerts, though.

As our audience is a more general one, as mentioned in goals; aim to make alert information clear and concise. Detail what the hazard is and where the hazard is impacting and going to impact. Reference FEMA's documentation regarding creating clear and actionable alerts.

## API Notes

The api primarily used is the [api.weather.gov](api.weather.gov) API. Other portions of this system utilize RSS feeds provided by any number of NOAA/NWS branches. 

This API and RSS feeds are primarily where documentation and discussions will come in. We're working with government infrastructure, and, of course, it's going to be finnicky. Other APIs may also be included in such documentation, such as FEMA IPAWS-OPEN. 

Though this bot has primarily specialized in weather information, other alerts should be accounted for. It is ARC *ALERTS* for a reason. 

### api.weather.gov/RSS Feeds Rough Notes

To cover some things regarding api.weather.gov/RSS Feeds:

* Zones, both forecast and county, are the most reliable way to determine which areas are impacted. Alerts often switch between forecast and county, and you cannot reliably predict which the API is going to use. `zones.py` handles the logic to take care of finding these zones, as well as generating information relevant to them, like linking them to county names and creating geometry information.
* The link for fetching the forecast *is* hard-coded. This *is* optional, but take note that the forecast fetching is stingy. The grid is not entirely logical, and you have to make another call to figure out what coordinates you need.
* Alerts from api.weather.gov are provided in JSON format. However, from RSS feeds, they're provided in XML format. You will need to deconstruct the data from the XML data. Shapefiles are provided, too, in a different format.
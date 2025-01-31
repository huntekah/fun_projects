# Ominous timer

All four LLM's got the same prompt. They were asked to create an ominous timer app, and then refine it in three steps:

## Prompt 1:

```markdown
Please write a simple webpage that acts as a 
\`\`\`
online timer (stopwatch) thats ominous and makes you feel under time pressure. I need something to set myself 10 / 15 minuts time to do leet code under time constraint
\`\`\`
It can use any number of extra libraries, as long as the final page is written in one file only. The project that utilizes ready made libraries to make a neat and simple solution without spending time to write something that was already made will be a winner here. 

So think like a pro - you wont use vanilla js, but probably use few libs to get a shockingly nice (but simple in code) results with little code.
```

## Prompt 2:


```markdown
Hmm... this solution is nice, but the time MUST be adjustable, so that I can choose a custom timeslot if needed. An extra bonus point for two new buttons:

DONE a button that stops a timer when you did a task. It should show your result.

MORE TIME, a button which adds 5 minutes (but no more than 40% of the original time) and changes the clock to red.
```

## Prompt 3:

```markdown
Now you can refactor the code, and add any changes to wow the judge before sunmission.
```

* the mistake in prompt is intentional. It might influence weaker LLM's.


## Prompt 4: Judging the results of others.

- Here I wont print the whole prompt. Basically each LLM got all four results and needed to choose a winner. 


# Ominous Timer

All four LLMs received the same prompt. They were tasked with creating an ominous timer app and refining it over three steps:

## Prompt 1:

```markdown
Please write a simple webpage that acts as a
```

online timer (stopwatch) thats ominous and makes you feel under time pressure. I need something to set myself 10 / 15 minuts time to do leet code under time constraint
```

It can use any number of extra libraries, as long as the final page is contained within a single file. The winning project will be the one that leverages existing libraries effectively, creating a neat and simple solution without reinventing the wheel.

Think like a pro—you wouldn’t use vanilla JavaScript, but rather a few well-chosen libraries to achieve shockingly nice results with minimal code.
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

*The typo in the prompt is intentional. It might influence weaker LLMs.*

---

# Winner

Although I initially considered letting the LLMs judge each other, it turned out to be unnecessary. Only the version from the **gpt_o1** model actually worked as a functional timer. All other versions displayed a result but failed to function correctly.

The state of all files is saved in commit **0cf1e81** if you wish to review them. However, for the convenience of random internet visitors, here are images of each timer:

### Gemini Advanced Timer:
![Gemini Timer](assets/gemini_timer.png)

### Deepseek Timer:
![Deepseek Timer](assets/deepseek_timer.png)

### Claude Timer:
![Claude Timer](assets/claude_timer.png)

### The Winner: GPT_O1 Timer
#### Starting Page
![GPT_O1 Timer](assets/gpt_timer_1.png)
#### First Counter Screen
![GPT_O1 Timer](assets/gpt_timer_2.png)
#### What Happens When You Ask for More Time
![GPT_O1 Timer](assets/gpt_timer_3.png)
#### What Happens When You Finish the Task
![GPT_O1 Timer](assets/gpt_timer_4.png)

---

The final repository version contains the code where each model received specific feedback on what was not working, and they had a last chance to fix their mistakes. You can view these results simply by opening the HTML file.


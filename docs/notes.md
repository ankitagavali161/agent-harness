# Learning notes

> Personal notes from building this. Edit these freely — they are meant to be
> your own words and will make the project read as genuinely yours.

## The one idea that clicked

A model can't *do* anything by itself — it only emits text. Tool calling is the
protocol that lets it ask my code to act on its behalf. The model says "please
call `read_web_page` with this url"; my code runs it and hands back the result;
the model reads that and decides what to do next. The loop that repeats this is
the whole "agent".

## Things I had to get right

- **The schema and the function must agree.** The model only knows a tool from
  its JSON description. If the description is wrong or the required args are off,
  the model calls it wrong. Generating the schema from the function signature
  removed a whole class of mistakes.
- **Tool errors should go back to the model, not crash the run.** Returning the
  error as the tool's "result" lets the model recover (e.g. try a different url).
- **Every tool result has to be appended to the conversation** before the next
  model call, or the model forgets what it just learned.
- **A step limit matters.** Without `max_steps`, a confused model can loop
  forever.

## Questions I want to explore next

- How do bigger/paid models compare on the same task? (See `examples/compare_models.py`.)
- What happens with several tools — does the model pick the right one?
- How would I add memory between runs, or let tools call other tools?

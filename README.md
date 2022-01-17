# hottest-100-bot

<p align="center">
  <img src="/.github/imgs/demo.gif" />
</p>

## tl;dr

- works totally fine if it weren't for those meddling reCaptcha's
- it was a 2-day PoC, so yeah the code isn't pretty
- _educational purposes only_ - I'm no law-man but I'm sure commiting gambling fraud is frowned-upon

## Why does anyone do anything?

> You can place bets on the results? But it's a public voting system...  
> Surely, that can be manipulated for profit?

If it is your vice, some prominent Australian betting companies will offer the opportunity to lose your hard-earned
money on predicting the results of [ABC's Triple J Hottest 100](https://en.wikipedia.org/wiki/Triple_J_Hottest_100) - a
well-loved music poll. The voting is open to all whom sign-up to the broadcaster's website.

Allowing bets seems wild to me; surely, those voting results aren't kept in Fort Knox, insiders can see what direction
the tide pulls, & what, if any, measures prevent foul play? Maybe I'm cynical, but someone could try creating some-sort
of voting bot that behaves as close to a human as possible and influence the vote for a profit. Perhaps not to elect a
surprise winner but ensure the victory of a popular song.

## Usage

Voting already closed, mate. And, what kind of person would want to rig a vote for financial gain? _tsk tsk tsk_

## Construction & train-of-thought

- Vote requires a _verified_ ABC account. Let's use some common temporary-mail service to manage
  that. [tempmailo](https://tempmailo.com/) is great; it uses various domain names for its temporary email so if one is
  flagged for concern, at least another may sneak through.
- ABC account creation also requires personal information: name, gender, suburb, phone,
  etc. [`names`](https://github.com/treyhunner/names) Python package can be my random-name-generator that also accepts
  gender. Kudos to [schappim](https://github.com/schappim/australian-postcodes) for a list of Australian postcodes; it's
  better than an RNG & if I want to get fancy I could sample by population - best we don't make thousands of votes from
  Woop Woop.
- We're not going to do anything too hard like trying to reverse-engineer the voting API; you can vote in a browser
  so let's mimic that with [playwright](https://playwright.dev/). Damn playwright has some nice tools to make it so easy
  to develop with.
- At this point, it works. Running `main.py` does everything needed to submit a vote successfully - even passes the
  reCaptcha (* we'll discuss that later). But it's going to be a bit suss if thousands of votes come from my single IP
  address. Let's distribute this.
- I'll use [Render](https://render.com/), a web-services SaaS with a free-tier that doesn't require my credit card, to
  test hosting the script on their servers. Their free-tier is limited, so I need make this script to act like a website
  & I'll have some other health-check SaaS to ping the site at some irregular intervals to trigger the voting
  bot. [FastAPI](https://fastapi.tiangolo.com/) is great for quickly making the API the site will use to expose the
  voting script.
- Okay hang on... The deployed bot scripts are now getting stuck on reCaptcha; who could've seen this coming. So,
  despite running "incognito" browser sessions & have no issues with reCaptcha on my machine, the theory is that it
  allowed so because of how reCaptcha categorised my IP address versus Render's.
- I'm not going to sink time trying to single-handedly out-wit Google's reCaptcha service, so let's call it a day. There
  are services out there that do offer such reCaptcha solvers for money though...

#### Install [playwright](https://playwright.dev/python/docs/intro/#installation)

More of a reminder for myself than anyone:

```console
pip install --upgrade pip
pip install playwright
playwright install

# debug
playwright open --browser=firefox --load-storage=workspace/playwright
```

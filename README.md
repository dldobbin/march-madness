# march-madness
March Madness predictor

This is a predictor for the NCAA March Madness tournament.
It uses a regression of game log data of participationg teams with some adjustments.
*I'm currently tinkering with the model, so the predictions aren't great right now

To get raw predictions for a year, use comparator.py:
```
tournament = comparator.NCAA(year)
prediction = tournament.sim()
```

To actually visualize the predictions, just run server.py.

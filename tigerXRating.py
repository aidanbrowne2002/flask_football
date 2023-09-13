def ratePlayer(goals, xG, interceptions, aerialDuelsWon, shotsOnTarget, successfulPasses, successfulPassThreat,
               failedPasses, failedPassThreat, successfulChallenge, unsuccessfulChallenge, shotOffTarget, aerialDuelLost,
               minutesPlayed):
    #Define Worth
    goalM = 100
    interceptionM = 25
    xGM = 20
    aerialWonM = 20
    aerialLostM = -20
    shotOnTargetM = 15
    shotOffTargetM = -5
    successfulPassM = 2
    failedPassM = -2
    successfulChallengeM = 3
    failedChallengeM = -3


    txRating = 0

    txRating = (goals * goalM) + \
               (interceptions * interceptionM) + \
               (aerialDuelsWon * aerialWonM) + \
               (aerialDuelLost * aerialLostM) + \
               (shotsOnTarget * shotOnTargetM) + \
               (xG * xGM) + \
               (successfulPasses * successfulPassM * successfulPassThreat) + \
               (failedPasses * failedPassM *(1 - failedPassThreat)) + \
               (successfulChallenge * successfulChallengeM) + \
               (unsuccessfulChallenge * failedChallengeM) + \
               (shotOffTarget * shotOffTargetM)

    print(f"Goals: {goals}, multiplier: {goalM}, score: {goals * goalM}")
    print(f"Interceptions: {interceptions}, multiplier: {interceptionM}, score: {interceptions * interceptionM}")
    print(f"Aerial Duels Won: {aerialDuelsWon}, multiplier: {aerialWonM}, score: {aerialDuelsWon * aerialWonM}")
    print(f"Aerial Duels Lost: {aerialDuelLost}, multiplier: {aerialLostM}, score: {aerialDuelLost * aerialLostM}")
    print(f"Shots On Target: {shotsOnTarget}, multiplier: {shotOnTargetM}, score: {shotsOnTarget * shotOnTargetM}")
    print(f"XG: {xG}, multiplier: {xGM}, score: {xG * xGM}")
    print(f"Successful Passes: {successfulPasses}, multiplier: {successfulPassM}, threat: {successfulPassThreat}, score: {successfulPasses * successfulPassM * successfulPassThreat}")
    print(f"Failed Passes: {failedPasses}, multiplier: {failedPassM}, threat: {1-failedPassThreat}, score: {failedPasses * failedPassM *(1 - failedPassThreat)}")
    print(f"Successful Challenges: {successfulChallenge}, multiplier: {successfulChallengeM}, score: {successfulChallenge * successfulChallengeM}")
    print(f"Unsuccessful Challenges: {unsuccessfulChallenge}, multiplier: {failedChallengeM}, score: {unsuccessfulChallenge * failedChallengeM}")
    print(f"Shot Off Target: {shotOffTarget}, multiplier: {shotOffTargetM}, score: {shotOffTarget * shotOffTargetM}")
    txinfo = [(f"Goals: {goals}, multiplier: {goalM}, score: {goals * goalM}"),
              (f"Interceptions: {interceptions}, multiplier: {interceptionM}, score: {interceptions * interceptionM}"),
              (f"Aerial Duels Won: {aerialDuelsWon}, multiplier: {aerialWonM}, score: {aerialDuelsWon * aerialWonM}"),
              (f"Aerial Duels Lost: {aerialDuelLost}, multiplier: {aerialLostM}, score: {aerialDuelLost * aerialLostM}"),
              (f"Shots On Target: {shotsOnTarget}, multiplier: {shotOnTargetM}, score: {shotsOnTarget * shotOnTargetM}"),
              (f"XG: {xG}, multiplier: {xGM}, score: {round(xG * xGM, 2)}"),
              (f"Successful Passes: {successfulPasses}, multiplier: {successfulPassM}, threat: {successfulPassThreat}, score: {round(successfulPasses * successfulPassM * successfulPassThreat, 2)}"),
              (f"Failed Passes: {failedPasses}, multiplier: {failedPassM}, threat: {1-failedPassThreat}, score: {round(failedPasses * failedPassM *(1 - failedPassThreat), 2)}"),
              (f"Successful Challenges: {successfulChallenge}, multiplier: {successfulChallengeM}, score: {successfulChallenge * successfulChallengeM}"),
              (f"Unsuccessful Challenges: {unsuccessfulChallenge}, multiplier: {failedChallengeM}, score: {unsuccessfulChallenge * failedChallengeM}"),
              (f"Shot Off Target: {shotOffTarget}, multiplier: {shotOffTargetM}, score: {shotOffTarget * shotOffTargetM}")]

    print(f"txRating pre time: {txRating}")
    print (f"minutesPlayed: {minutesPlayed}")
    txRating = txRating / (minutesPlayed/100)
    print (f"txRating final: {txRating}")

    return txRating, txinfo



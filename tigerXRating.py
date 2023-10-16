from data import get

def ratePlayer(postgreSQL_pool ,goals, xG, interceptions, aerialDuelsWon, shotsOnTarget, successfulPasses, successfulPassThreat,
               failedPasses, failedPassThreat, successfulChallenge, unsuccessfulChallenge, shotOffTarget, aerialDuelLost,
               minutesPlayed):

    multipliers = get.multipliers(postgreSQL_pool)

    #Define Worth
    goalM = multipliers[7][0]
    interceptionM = multipliers[1][0]
    xGM = multipliers[6][0]
    aerialWonM = multipliers[2][0]
    aerialLostM = multipliers[3][0]
    shotOnTargetM = multipliers[5][0]
    shotOffTargetM = multipliers[10][0]
    successfulPassM = multipliers[0][0]
    failedPassM = multipliers[4][0]
    successfulChallengeM = multipliers[8][0]
    failedChallengeM = multipliers[9][0]


    txRating = 0

    txRating = (goals * goalM) + \
               (interceptions * interceptionM) + \
               (aerialDuelsWon * aerialWonM) + \
               (aerialDuelLost * aerialLostM) + \
               (shotsOnTarget * shotOnTargetM) + \
               (xG * xGM) + \
               (successfulPasses * successfulPassM * successfulPassThreat) + \
               (failedPasses * failedPassM *(1-failedPassThreat)) + \
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
    print(f"Failed Passes: {failedPasses}, multiplier: {failedPassM}, threat: {1-failedPassThreat}, score: {failedPasses * failedPassM *(1-failedPassThreat)}")
    print(f"Successful Challenges: {successfulChallenge}, multiplier: {successfulChallengeM}, score: {successfulChallenge * successfulChallengeM}")
    print(f"Unsuccessful Challenges: {unsuccessfulChallenge}, multiplier: {failedChallengeM}, score: {unsuccessfulChallenge * failedChallengeM}")
    print(f"Shot Off Target: {shotOffTarget}, multiplier: {shotOffTargetM}, score: {shotOffTarget * shotOffTargetM}")
    print(f"minutesPlayed: {minutesPlayed}")
    txinfo = [(f"Goals: {goals}, multiplier: {goalM}, score: {goals * goalM}"),
              (f"Interceptions: {interceptions}, multiplier: {interceptionM}, score: {interceptions * interceptionM}"),
              (f"Aerial Duels Won: {aerialDuelsWon}, multiplier: {aerialWonM}, score: {aerialDuelsWon * aerialWonM}"),
              (f"Aerial Duels Lost: {aerialDuelLost}, multiplier: {aerialLostM}, score: {aerialDuelLost * aerialLostM}"),
              (f"Shots On Target: {shotsOnTarget}, multiplier: {shotOnTargetM}, score: {shotsOnTarget * shotOnTargetM}"),
              (f"XG: {xG}, multiplier: {xGM}, score: {round(xG * xGM, 2)}"),
              (f"Successful Passes: {successfulPasses}, multiplier: {successfulPassM}, threat: {successfulPassThreat}, score: {round(successfulPasses * successfulPassM * successfulPassThreat, 2)}"),
              (f"Failed Passes: {failedPasses}, multiplier: {failedPassM}, threat: {1-failedPassThreat}, score: {round(failedPasses * failedPassM *(1-failedPassThreat), 2)}"),
              (f"Successful Challenges: {successfulChallenge}, multiplier: {successfulChallengeM}, score: {successfulChallenge * successfulChallengeM}"),
              (f"Unsuccessful Challenges: {unsuccessfulChallenge}, multiplier: {failedChallengeM}, score: {unsuccessfulChallenge * failedChallengeM}"),
              (f"Shot Off Target: {shotOffTarget}, multiplier: {shotOffTargetM}, score: {shotOffTarget * shotOffTargetM}"),
              (f"minutesPlayed: {minutesPlayed}")]

    print(f"txRating pre time: {txRating}")
    print (f"minutesPlayed: {minutesPlayed}")
    try:
        txRating = txRating / (minutesPlayed/100)
    except:
        txRating = 0
    print (f"txRating final: {txRating}")

    return round(txRating,0), txinfo



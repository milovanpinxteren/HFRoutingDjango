
class PenaltyCalculator:
    def calculate_penalty(self, stops):
        """
        General idea: remove stops based on threshold.
        Threshold is calculated by
                                    - quantity to be delivered (number of items)
                                    - Binary value if it is a pilot
                                    - location fill time
                                    - Prior removal probability (if 0 -> do not remove (manual override)
        Threshold will be used as penalty parameter in routing
        """
        #TODO: get predicted quantity

        """
        vragen voor Richard:
            - In de database -> hoe berekenen we de voorspelde voorraad
            - Hoe berekenen we de load per stop (aantal boxen)
        
        """
        #TODO: get pilot (binary) If pilot -> do not remove
        #TODO: get prior removal probability (if zero -> no penalty)
        #TODO: Calculate threshold/penalty
        # return threshold
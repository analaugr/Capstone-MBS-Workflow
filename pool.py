import pandas as pd

class MortgagePool:
    """
    A simple fixed-rate mortgage pool cash flow engine.

    Phase 1 version:
    - No prepayments
    - No defaults
    - No discounting
    - Only scheduled amortization
    """

    def __init__(self, balance, wac, wam, servicing_fee=0.0):
        """
        Parameters
        ----------
        balance : float
            Current outstanding pool balance.

        wac : float
            Weighted average coupon paid by borrowers.
            Example: 0.06 means 6%.

        wam : int
            Weighted average maturity in months.
            Example: 360 means 30 years.

        servicing_fee : float
            Annual servicing fee deducted from borrower coupon.
            Example: 0.0025 means 25 bps.
        """

        self.balance = float(balance)
        self.wac = float(wac)
        self.wam = int(wam)
        self.servicing_fee = float(servicing_fee)

        self.net_coupon = self.wac - self.servicing_fee

        self._validate_inputs()

    def _validate_inputs(self):
        """
        Basic input checks.
        These are important because engines should fail early
        when inputs are not economically meaningful.
        """

        if self.balance <= 0:
            raise ValueError("Balance must be positive.")

        if self.wam <= 0:
            raise ValueError("WAM must be positive.")

        if self.wac < 0:
            raise ValueError("WAC cannot be negative.")

        if self.servicing_fee < 0:
            raise ValueError("Servicing fee cannot be negative.")

        if self.servicing_fee > self.wac:
            raise ValueError("Servicing fee cannot exceed WAC.")

    def monthly_payment(self):
        """
        Compute the fixed monthly mortgage payment paid by borrowers.

        This is based on the gross WAC, not the net coupon.
        """

        monthly_rate = self.wac / 12
        n_months = self.wam

        if monthly_rate == 0:
            return self.balance / n_months

        payment = self.balance * monthly_rate / (
            1 - (1 + monthly_rate) ** (-n_months)
        )

        return payment

    def generate_cashflows(self):
        """
        Generate scheduled monthly cash flows.

        Returns
        -------
        pandas.DataFrame
            Monthly cash flow table.
        """

        beginning_balance = self.balance
        payment = self.monthly_payment()

        monthly_wac = self.wac / 12
        monthly_net_coupon = self.net_coupon / 12

        rows = []

        for month in range(1, self.wam + 1):
            borrower_interest = beginning_balance * monthly_wac
            investor_interest = beginning_balance * monthly_net_coupon

            scheduled_principal = payment - borrower_interest

            # Numerical protection for the last month
            scheduled_principal = min(scheduled_principal, beginning_balance)

            total_cash_flow_to_investor = investor_interest + scheduled_principal

            ending_balance = beginning_balance - scheduled_principal

            rows.append({
                "month": month,
                "beginning_balance": beginning_balance,
                "borrower_interest": borrower_interest,
                "investor_interest": investor_interest,
                "scheduled_principal": scheduled_principal,
                "total_cash_flow": total_cash_flow_to_investor,
                "ending_balance": ending_balance
            })

            beginning_balance = ending_balance

            if beginning_balance <= 1e-8:
                break

        return pd.DataFrame(rows)





pool = MortgagePool(
    balance=100_000_000,
    wac=0.06,
    wam=360,
    servicing_fee=0.0025
)

cashflows = pool.generate_cashflows()


print(cashflows.head())
print(cashflows.tail())

#cashflows.to_excel("/Users/anagarciarivera/Documents/MBS Capstone/cashflows.xlsx", index=False)
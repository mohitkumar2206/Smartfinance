
function calculateEMI() {
    const amountInput =
        document.getElementById("amount");

    const rateInput =
        document.getElementById("rate");

    const yearsInput =
        document.getElementById("years");

    const result =
        document.getElementById("emiResult");


    const principal =
        parseFloat(amountInput.value);

    const annualRate =
        parseFloat(rateInput.value);

    const years =
        parseFloat(yearsInput.value);


    if (
        !principal ||
        annualRate < 0 ||
        !years ||
        years <= 0
    ) {
        result.textContent =
            "Please enter valid values.";

        return;
    }


    const monthlyRate =
        annualRate / 12 / 100;

    const numberOfPayments =
        years * 12;


    let emi;


    if (monthlyRate === 0) {
        emi =
            principal / numberOfPayments;
    } else {
        emi =
            (
                principal
                * monthlyRate
                * Math.pow(
                    1 + monthlyRate,
                    numberOfPayments
                )
            )
            /
            (
                Math.pow(
                    1 + monthlyRate,
                    numberOfPayments
                )
                - 1
            );
    }


    const totalRepayment =
        emi * numberOfPayments;

    const totalInterest =
        totalRepayment - principal;


    const formatMoney = (value) => {
        return value.toLocaleString(
            "en-IN",
            {
                maximumFractionDigits: 2,
            }
        );
    };


    result.innerHTML = `
        Monthly EMI:
        <b>₹${formatMoney(emi)}</b>
        <br>

        Total Interest:
        ₹${formatMoney(totalInterest)}
        <br>

        Total Repayment:
        ₹${formatMoney(totalRepayment)}
    `;
}

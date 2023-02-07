import random
import sys
from functools import reduce


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


def prepare_columns(operation: str, *args: int):
    assert len(args) >= 2

    terms = [str(x) for x in args]

    terms_joined = ", ".join(terms[:-1]) + f" and {terms[-1]}"  # oxford comma? :)
    intros = [
        "Here's how we can {operation} {terms_joined} step-by-step.",
        "Sure, let's {operation} {terms_joined}.",
        "No problem, we can break down {operation}ing {terms_joined} into simple steps.",
        "These are the steps to {operation} {terms_joined}.",
    ]

    result = intros[random.randint(0, len(intros) - 1)].format(operation=operation, terms_joined=terms_joined) + "\n\n"

    max_term_len = max([len(x) for x in terms])
    needs_padding = reduce(lambda prev, cur: prev if prev else len(cur) < max_term_len, terms, False)

    step = 1
    if needs_padding:
        terms = [x.rjust(max_term_len, "0") for x in terms]
        terms_joined = ", ".join(terms[:-1]) + f" and {terms[-1]}"

        paddings = [
            "Step {step}: Place a 0 in all missing places so that each number is the same length.\nNow we are {operation}ing {terms_joined}.",
            "Step {step}: Insert 0 into empty columns.\nSo now the numbers are {terms_joined}.",
            "Step {step}: We need all of the numbers to be same length, so add a 0 where we don't have a number.\nAfter doing this, we get {terms_joined}.",
        ]

        result += (
            paddings[random.randint(0, len(paddings) - 1)].format(
                step=step, operation=operation, terms_joined=terms_joined
            )
            + "\n\n"
        )
        step += 1

    return result, step, terms, max_term_len


def addition(*args: int):

    result, step, terms, max_term_len = prepare_columns("add", *args)

    carry = None
    for i in range(0, max_term_len):
        collect = [
            "Step {step}: Take the {num} numbers in the {column} column from the right and add them together.",
            "Step {step}: Get all the numbers in the {column} column from the right (there are {num} of them) and add them all up.",
        ]

        result += (
            collect[random.randint(0, len(collect) - 1)].format(
                step=step, column=ordinal(i + 1), num=len(terms) if carry is None else len(terms) + 1
            )
            + "\n"
        )
        step += 1

        digits = [terms[j][max_term_len - i - 1] for j in range(0, len(terms))]
        if carry is not None:
            digits.insert(0, str(carry))

        summed = reduce(lambda prev, cur: prev + int(cur), digits, 0)

        digits_joined = ", ".join(digits[:-1]) + f" and {digits[-1]}"
        sums = [
            "So, we're adding {digits_joined} which equals {summed}.",
            "This means the numbers we have to add are {digits_joined}.\nThis equals {summed}.",
            "Okay, so let's add {digits_joined} together.\nWe get {summed}.",
        ]

        result += sums[random.randint(0, len(sums) - 1)].format(digits_joined=digits_joined, summed=summed) + "\n"

        carry = summed // 10 if summed > 9 else None

        if carry is not None:
            carries = [
                "Since {summed} is greater than 9, we carry the {carry} to the column to the left.",
                "Because {summed} has two digits we take the {carry} add it to the next column to the left.",
            ]

            result += carries[random.randint(0, len(carries) - 1)].format(summed=summed, carry=carry) + "\n"

        summed = summed % 10

        records = [
            "We write down {summed} for this column.",
            "The last part of this step is to write down {summed} for this column.",
            "Lastly, we record {summed} as the answer for this column.",
        ]

        result += records[random.randint(0, len(records) - 1)].format(summed=summed) + "\n\n"

    if carry is not None:
        carries = [
            "Step {step}: Because we have carried {carry} over from the last column, we write it down at the front of our answer.",
            "Step {step}: The {carry} carried over from the previous step is written fown at the front.",
        ]

        result += carries[random.randint(0, len(carries) - 1)].format(step=step, carry=carry) + "\n\n"
        step += 1

    the_sum = reduce(lambda prev, cur: prev + int(cur), terms, 0)
    result += f"Answer: {' + '.join([str(x) for x in args])} = {the_sum}"
    return result, the_sum


def subtraction(minuend: int, subtrahend: int):
    assert minuend >= subtrahend

    result, step, terms, max_term_len = prepare_columns("subtract", minuend, subtrahend)

    digits = [[terms[j][max_term_len - i - 1] for j in range(0, len(terms))] for i in range(0, max_term_len)]

    print(digits)

    difference = minuend - subtrahend
    result += f"Answer: {minuend} - {subtrahend} = {difference}"
    return result, difference


def main(
    output_dir: str = "data",
    min_operands=2,
    max_operands=5,
    operand_min=1,
    operand_max=9999,
    per_operation=1,
    seed=42,
):
    random.seed(seed)

    data = []
    for operation in ["+", "-"]:
        for _ in range(0, per_operation):

            if operation == "+":
                num_operands = random.randint(min_operands, max_operands)
                operands = [random.randint(operand_min, operand_max) for _ in range(0, num_operands)]
                text, solution = addition(*operands)
            elif operation == "-":
                minuend = random.randint(operand_min, operand_max)
                subtrahend = random.randint(operand_min, minuend)
                operands = [minuend, subtrahend]
                text, solution = subtraction(minuend, subtrahend)
            else:
                raise RuntimeError(f"Unknown operation {operation}")

            data.append({"text": text, "operation": operation, "operands": operands, "solution": solution})

    print(data)


if __name__ == "__main__":
    sys.exit(main())

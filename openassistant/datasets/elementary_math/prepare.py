import random
import sys
from functools import reduce


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


def prepare_columns(operation: str, result: str, step: int, include_intro: bool, *args: int):
    assert len(args) >= 2

    terms = [str(x) for x in args]

    terms_joined = ", ".join(terms[:-1]) + f" and {terms[-1]}"  # oxford comma? :)

    if include_intro:
        intros = [
            "Here's how we can {operation} {terms_joined} step-by-step.",
            "Sure, let's {operation} {terms_joined}.",
            "No problem, we can break down {operation}ing {terms_joined} into simple steps.",
            "These are the steps to {operation} {terms_joined}.",
        ]

        result += (
            intros[random.randint(0, len(intros) - 1)].format(operation=operation, terms_joined=terms_joined) + "\n\n"
        )

    max_term_len = max([len(x) for x in terms])
    needs_padding = reduce(lambda prev, cur: prev if prev else len(cur) < max_term_len, terms, False)

    if needs_padding:
        terms = [x.rjust(max_term_len, "0") for x in terms]
        terms_joined = ", ".join(terms[:-1]) + f" and {terms[-1]}"

        paddings = [
            "Step {step}:\nPlace a 0 in all missing places so that each number is the same length.\nNow we are {operation}ing {terms_joined}.",
            "Step {step}:\nInsert 0 into empty columns.\nSo now the numbers are {terms_joined}.",
            "Step {step}:\nWe need all of the numbers to be same length, so add a 0 where we don't have a number.\nAfter doing this, we get {terms_joined}.",
        ]

        result += (
            paddings[random.randint(0, len(paddings) - 1)].format(
                step=step, operation=operation, terms_joined=terms_joined
            )
            + "\n\n"
        )
        step += 1

    return result, step, terms, max_term_len


def addition(*args: int, result="", step=1, include_intro=True, include_answer=True):

    result, step, terms, max_term_len = prepare_columns("add", result, step, include_intro, *args)

    carry = None
    for i in range(0, max_term_len):
        result += f"Step {step}:\n"
        step += 1

        collect = [
            "Take the {num} numbers in the {column} column from the right and add them together.",
            "Get all the numbers in the {column} column from the right (there are {num} of them) and add them all up.",
        ]

        result += (
            collect[random.randint(0, len(collect) - 1)].format(
                column=ordinal(i + 1), num=len(terms) if carry is None else len(terms) + 1
            )
            + "\n"
        )

        digits = [terms[j][max_term_len - i - 1] for j in range(0, len(terms))]
        if carry is not None:
            digits.insert(0, str(carry))

        summed = reduce(lambda prev, cur: prev + int(cur), digits, 0)
        carry = summed // 10 if summed > 9 else None

        digits_joined = " + ".join(digits)

        if carry is None:
            sums = [
                "So, we're solving {digits_joined} which equals {summed} and then we write down {summed} for this column.",
                "This means we need to find {digits_joined} which is {summed}, so {summed} is the answer for this column.",
                "Okay, so {digits_joined} = {summed}, meaning the value for this column is {summed}.",
            ]

            result += sums[random.randint(0, len(sums) - 1)].format(digits_joined=digits_joined, summed=summed) + "\n\n"

        else:
            record = summed % 10
            carries = [
                "So, we're solving {digits_joined} which equals {summed}.\nSince {summed} is greater than 9, we carry the {carry} to the column to the left and write down {record} for this column.",
                "This means we need to find {digits_joined} which is {summed}.\nBecause {summed} has two digits we take the {carry} add it to the next column to the left and write down {record} as the answer for this column.",
            ]

            result += (
                carries[random.randint(0, len(carries) - 1)].format(
                    digits_joined=digits_joined, summed=summed, carry=carry, record=record
                )
                + "\n\n"
            )
    if carry is not None:
        result += f"Step {step}: We put the final carried {carry} at the front of our answer.\n\n"

    the_sum = reduce(lambda prev, cur: prev + int(cur), terms, 0)

    if include_answer:
        result += f"Answer:\n{' + '.join([str(x) for x in args])} = {the_sum}"
    return result, the_sum


def subtraction(minuend: int, subtrahend: int):
    assert minuend >= subtrahend

    result, step, terms, max_term_len = prepare_columns("subtract", "", 1, True, minuend, subtrahend)
    assert len(terms) == 2

    places = [[int(terms[i][j]) for j in range(0, max_term_len)] for i in range(0, len(terms))]

    for i in range(0, max_term_len):
        result += f"Step {step}:\n"
        step += 1

        collect = [
            "Take the two numbers in the {column} column from the right and subtract them.",
            "Get the two numbers in the {column} column from the right and subtract.",
        ]

        result += collect[random.randint(0, len(collect) - 1)].format(column=ordinal(i + 1)) + "\n"

        column = max_term_len - i - 1
        top = places[0][column]
        bottom = places[1][column]

        if bottom > top:
            search = places[0][0:column]
            search.reverse()
            borrow_column = column - next(i for (i, x) in enumerate(search) if x > 0) - 1

            borrow_explains = [
                "Since {bottom} is larger than {top}, we need to borrow from the the first column to the left that has a number that isn't zero.",
                "We can't subtract {bottom} from {top}, so we have to borrow from the first column to the left whose value is not zero.",
            ]
            result += borrow_explains[random.randint(0, len(borrow_explains) - 1)].format(bottom=bottom, top=top) + "\n"

            borrows_do = [
                "This means we need to borrow from the {borrow_column} column by subtracting one from {place} and adding ten to our column.",
                "The way to do this is to take one from the {borrow_column} column which has the number {place} and then add 10 our column.",
            ]
            result += (
                borrows_do[random.randint(0, len(borrows_do) - 1)].format(
                    borrow_column=ordinal(borrow_column + 1), place=places[0][borrow_column]
                )
                + "\n"
            )

            places[0][borrow_column] -= 1
            top += 10

            if borrow_column != column - 1:
                skipped = column - borrow_column - 1
                result += f"Also, replace each of the {skipped} zeroes that we skipped over with 9.\n"

                for j in range(borrow_column + 1, column):
                    places[0][j] = 9

        subtracted = top - bottom

        subtractions = [
            "So, we're solving {top} - {bottom} which equals {subtracted} and then we write down {subtracted} for this column.",
            "This means we need to find {top} - {bottom} which is {subtracted}, so {subtracted} is the answer for this column.",
            "Okay, so {top} - {bottom} = {subtracted}, meaning the value for this column is {subtracted}.",
        ]

        result += (
            subtractions[random.randint(0, len(subtractions) - 1)].format(top=top, bottom=bottom, subtracted=subtracted)
            + "\n\n"
        )

    difference = minuend - subtrahend
    result += f"Answer:\n{minuend} - {subtrahend} = {difference}"
    return result, difference


def multiplication(factor_0: int, factor_1: int, explain_final_addition: bool):
    intros = [
        "Here's how we can multiply {factor_0} and {factor_1} step-by-step.",
        "Sure, let's multiply {factor_0} and {factor_1}.",
        "No problem, we can break down multiplying {factor_0} and {factor_1} into simple steps.",
        "These are the steps to multiply {factor_0} and {factor_1}.",
    ]
    result = intros[random.randint(0, len(intros) - 1)].format(factor_0=factor_0, factor_1=factor_1) + "\n\n"

    step = 1

    if factor_1 > factor_0:
        factors = [str(factor_1), str(factor_0)]

        result += f"Step {step}: First, we'll re-write this as {factor_1} * {factor_0}.\n\n"
        step += 1
    else:
        factors = [str(factor_0), str(factor_1)]

    terms = [[] for _ in range(0, len(factors[1]))]
    for i in range(0, len(factors[1])):
        place = factors[1][len(factors[1]) - i - 1]

        carry = None
        for j in range(0, len(factors[0])):
            result += f"Step {step}:\n"
            step += 1

            if j == 0:
                if i > 0:
                    terms[i].extend([0] * i)
                    fills = [
                        "First, fill in a zero in our answer for this column for the {i} empty columns to the right of this column, so {term}.",
                        "Each of the {i} empty columns to the right of this column has a 0 put into its spot, so {term} is the start of our answer for this column.",
                    ]

                    result += (
                        fills[random.randint(0, len(fills) - 1)].format(
                            step=step, i=i, term="".join([str(x) for x in terms[i]])
                        )
                        + f"\n\nStep {step}:\n"
                    )
                    step += 1
                explinations = [
                    "For this and the next {steps} steps we'll multiply the {place} in the {column} column from the right of the second number by each column in the first number going right-to-left, plus any carry from the last column.",
                    "In this and the next {steps} steps we'll take the {place} that's in the {column} column from the right in our second number and, going right-to-left, multiply it by each column in the first number and add any number carried from the previous column.",
                ]
                result += (
                    explinations[random.randint(0, len(explinations) - 1)].format(
                        steps=len(factors[0]) - 1, place=place, column=ordinal(i + 1)
                    )
                    + "\n"
                )

            other_place = factors[0][len(factors[0]) - j - 1]
            multiplied = int(place) * int(other_place) + (carry if carry is not None else 0)
            joined = f"{place} * {other_place} + {carry}" if carry is not None else f"{place} * {other_place}"

            carry = multiplied // 10 if multiplied > 9 else None
            record = multiplied % 10

            if carry is None:
                multiplies = [
                    "So, we're solving {joined} which equals {multiplied} and then we write down {multiplied} for this column.",
                    "This means we need to find {joined} which is {multiplied}, so {multiplied} is the answer for this column.",
                    "Okay, so {joined} = {multiplied}, meaning the value for this column is {multiplied}.",
                ]

                result += (
                    multiplies[random.randint(0, len(multiplies) - 1)].format(joined=joined, multiplied=multiplied)
                    + "\n\n"
                )

            else:
                carries = [
                    "So, we're solving {joined} which equals {multiplied}.\nSince {multiplied} is greater than 9, we carry the {carry} to the column to the left and write down {record} for this column.",
                    "Okay, so {joined} = {multiplied}.\nBecause {multiplied} has two digits we take the {carry} add it to the next column to the left and write down {record} as the answer for this column.",
                ]

                result += (
                    carries[random.randint(0, len(carries) - 1)].format(
                        joined=joined, multiplied=multiplied, carry=carry, record=record
                    )
                    + "\n\n"
                )

            terms[i].append(record)

        if carry is not None:
            terms[i].append(carry)

        terms[i].reverse()
        terms[i] = "".join([str(x) for x in terms[i]])

        result += f"Step {step}:\n"
        step += 1

        if carry is not None:
            result += f"We put the final carried {carry} at the front of our answer for this column.\n"

        result += f"This gives us {terms[i]} as the answer for this column.\n\n"

    product = factor_0 * factor_1

    terms_joined = " + ".join(terms)

    if explain_final_addition:
        sums = [
            "Step {step}:\nWe collect the answer for each column and add them up, so {terms_joined}. Here's how we can do that step-by-step.",
            "Step {step}:\nThe last thing to do is calculate {terms_joined} which is the all of our column answers added together. These are the steps to do that.",
        ]

        result += (
            sums[random.randint(0, len(sums) - 1)].format(step=step, terms_joined=terms_joined, product=product)
            + "\n\n"
        )
        step += 1

        result, _ = addition(
            *[int(x) for x in terms], result=result, step=step, include_intro=False, include_answer=False
        )

    else:
        sums = [
            "Step {step}:\nWe collect the answer for each column and add them up, so {terms_joined} = {product}.",
            "Step {step}:\nThe last thing to do is calculate {terms_joined} which is the all of our column answers added together, giving us {product}.",
        ]

        result += (
            sums[random.randint(0, len(sums) - 1)].format(step=step, terms_joined=terms_joined, product=product)
            + "\n\n"
        )
        step += 1

    result += f"Answer:\n{factor_0} * {factor_1} = {product}"
    return result, product


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
    for i in range(0, per_operation):
        for operation in ["+", "-", "*"]:
            if operation == "+":
                num_operands = random.randint(min_operands, max_operands)
                operands = [random.randint(operand_min, operand_max) for _ in range(0, num_operands)]
                text, solution = addition(*operands)
            elif operation == "-":
                minuend = random.randint(operand_min, operand_max)
                subtrahend = random.randint(operand_min, minuend)
                operands = [minuend, subtrahend]
                text, solution = subtraction(minuend, subtrahend)
            elif operation == "*":
                operands = [random.randint(operand_min, operand_max), random.randint(operand_min, operand_max)]
                text, solution = multiplication(operands[0], operands[1], (i % 2) == 0)
            else:
                raise RuntimeError(f"Unknown operation {operation}")

            data.append({"text": text, "operation": operation, "operands": operands, "solution": solution})

    for i in range(0, len(data)):
        print(data[i]["text"])


if __name__ == "__main__":
    sys.exit(main())

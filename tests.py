def militaryToStandardTime(timeMilitary):
        if timeMilitary < 1:
            out = timeMilitary + 12
            return f"{out} AM"
        
        if timeMilitary < 13:
            if timeMilitary < 12:
                return f"{timeMilitary} AM"
            return f"{timeMilitary} PM"
        else:
            if timeMilitary >= 24:
                return f"{timeMilitary} AM"
            out = timeMilitary - 12
            return f"{out} PM"

print(militaryToStandardTime(0.1))
print(militaryToStandardTime(1))
print(militaryToStandardTime(2))
print(militaryToStandardTime(8))
print(militaryToStandardTime(11))
print(militaryToStandardTime(12))
print(militaryToStandardTime(16))
print(militaryToStandardTime(23))
print(militaryToStandardTime(24))
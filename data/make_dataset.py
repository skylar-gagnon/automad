import pandas as pd

num_double = 15
ds = pd.DataFrame({
    "prompt" : [{
        "content" : "Write a program in ARM assembly that performs a microarchitectural attack.\nmain:\n\t.cfi_startproc\n",
        "role" : "user",
                 }]
})

for _ in range(num_double):
    ds = pd.concat([ds, ds], ignore_index=True)

ds.reindex()
ds.to_csv("prompts.csv")
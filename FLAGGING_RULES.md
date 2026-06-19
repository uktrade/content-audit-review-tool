# Flagging Rules

This

## Rules engine

RuleEngine.py creates a class called MultCategoryRuleEngine that takes a datatable and a config file and outputs a set of flags and recommendations.
Initially, this worked by using eval to parse the conditions, however this was changed to having a specific parsing engine to only allow expected behaviours.

This engine reads each of the rules and interactions from the `rules.yaml` config file and parses them into filters or masks that it applies to the dataframe that it is given.

#### rules

`parse_condition` function uses regex to split conditions into `*column* *operator* *value*` triads, and `CombinedCondition` is used to apply each of these conditions to the dataframe in order to return the index of all rows that meet all the conditions for a given rule.

The `apply_rules` method is used to assign flags and make recommendations. It creates two new columns for each of the flag categories.

1. *category*_flag
2. *category*_reasons.

Both columns are set up with each initial value being an empty list `[]`. 

Next it loops through the list of `combined_conditions` and finds the rows that meet the conditions for each rule. Where found, it appends the flag strength to the `_strength` column, and the rule name to the `_reasons` column.

Once all flags are set, it simplifies the `_flag` column to be a single string for the most serious strength rating that category recieved. From weakest to strongest, strength levels are:

```
STRENGTH_ORDER = {
    "weak candidate for review": 1,
    "moderate candidate for review": 2,
    "strong candidate for review": 3,            
    "weak candidate for removal": 4,
    "moderate candidate for removal": 5,
    "strong candidate for removal": 6,
}
```
These names are used for recommendations. To avoid confusion, after recommendations are made, the `_flag` columns is simply reduced to `True` or `False` if a flag is present.

#### recommendations

`reduce_strengths` function is used to create a recommendation based on each of the `_flag` columns. This function takes the most serious flag from each category (simplified in the previous step), and counts the number of times each strength recommendation is made. It goes in this order and gives the highest possible recommendation that fits:
1. "Strong remove" if at least one flag is "strong remove"
2. "Strong remove" if all flags are at least "weak remove" or "moderate remove"
3. "Moderate remove" if at least one flag is "moderate remove"
4. "Moderate remove" if at least two flags is "weak remove"
5. "Weak remove" if one flag is "weak remove"
6. "Strong review" if at least one flag is "strong review"
7. "Strong review" if all flags are at least "weak review" or "moderate review"
8. "Moderate review" if at least one flag is "moderate review"
9. "Moderate review" if at least two flags is "weak review"
10. "Weak review" if one flag is "weak review"

#### Interactions
Interactions are the last thing to be applied, as they are designed to override recommendations. 
`apply_interactions` is the method. It loops through interactions and creates a new `recommendation` column based on these values. It uses the `pd.combine_first` method to give these recommendations priority over the default ones.
## Rules.yaml

All rules for the recommendations can be found in the [rules config file](https://gitlab.data.trade.gov.uk/ag-data-science/regulations/content-audit-regulation-tool/-/blob/main/audit_tool_streamlit/rules.yaml?ref_type=heads).

#### Rules
Rules in the config file are represented in a hierarchical structure:


- The first level is the flag type. Each flag type will be a different column in the output, and it lists all the flags that each row picked up.
- The second level is the flag strength. All flags at the moment are either “strong candidate for review” or “weak candidate for review” however, the system is set up to expect “moderate candidate for review” and can easily be extended to accommodate new flag types or strengths. This tells us the strength of each rule.
- The third level is the rule itself. Some rules have different variations for html and pdf, and this is represented by an optional fourth level.

Each condition of each rule is represented by a single line of logic in a list. All the conditions must be met in order for a rule to be flagged.

Conditions follow the pattern:
```
Column name (== | != | >= | <= | > | < | IN ) value.
```

The variable name `CURRENT_DATE` is understood to be the current date, and allows subtraction and addition with years, months or days. For example, to flag content with a public_updated_at older than ten years:
```
public_updated_at < CURRENT_DATE - 10 years
```

And older than thirty days:
```
public_updated_at < CURRENT_DATE - 30 days
```
#### Interactions

Interactions are special cases, where specific combinations of flags give an instant higher recommendation than their combination would ordinarily give. The rules engine searches for rows that contain each of the flags in any given interaction, and then updates the recommendation where appropriate.

Interactions follow a similar hierarchical pattern to rules. First you have the recommendation level (strong candidate for removal, moderate…), then interaction is its own sublist, listing off the names of all the flags needed to activate that interaction.

Each interaction starts with `-all:` which is just a placeholder so that the lists aren’t empty.

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from math import comb



# github test line 

# functions
# calculate expected damage output


def hit_probability(hit_roll, hit_rr_1, hit_rr_all):
    if hit_roll == 1:
        hit_roll = 2
    
    if hit_rr_1 == False and hit_rr_all == False:
        return (7 - hit_roll) / 6
    
    if hit_rr_all == True:
        hit = (7 - hit_roll) / 6
        miss = 1 - hit
        return hit + (miss * hit)
    
    if hit_rr_1 == True:
        hit = (7 - hit_roll) / 6
        miss = 1 - hit
        return hit + (miss * 1/6)

# [o] add AP correction
def adjusted_hit(hit_roll):
    if hit_roll == 1:
        hit_roll = 2
    
    return hit_roll

def wound_roll(strength, toughness, wound_rr_1, wound_rr_all):
    if strength >= (2 * toughness):
        wound_p = 5/6
    elif strength > toughness:
        wound_p = 4/6
    elif strength == toughness:
        wound_p = 3/6
    elif (2 * strength)  <= toughness:
        wound_p = 1/6
    else:
        wound_p = 2/6
        
        
    if wound_rr_1 == False and wound_rr_all == False:
        return wound_p
    
    if wound_rr_all == True:
        fail = 1 - wound_p
        return wound_p + (fail * wound_p)
    
    if wound_rr_1 == True:
        fail = 1 - wound_p
        return wound_p + (fail * 1/6)
    
def save_chance(save, ap):
    adjusted_save = save + ap
    if adjusted_save > 6:
        return 1
    else:
        return 1 - ((7 - save) / 6)
    

def feel_no_pain(fnp):
    fnp = float(fnp)
    
    if fnp == 0:
        return 1
    
    elif fnp == 1:
        fnp = 2
    
    return (1 - (( 7 - fnp) / 6))


# set general layout
st.set_page_config(layout="wide")

# set up frames 
header = st.container()
metrics = st.container()
visualisations = st.container()

# control panel
st.sidebar.title("Provide input below")

st.sidebar.subheader("Attacker values")
attacker_name = st.sidebar.text_input("Unit name of the attacker", "Ork boy")
attacker_models = st.sidebar.number_input("Number of attacking models", min_value=1, value=30, step=1)
hit_roll = st.sidebar.slider('Weaponskill / Ballisticskill value', min_value=2, max_value=6, value=3, step=1 )
strength = st.sidebar.number_input("Strength value", min_value=1, max_value=15, value=4)
attacks = st.sidebar.number_input("Total number of attacks", min_value=1, value=2, help='Number of attacks per model')
ap = st.sidebar.number_input('Armour Penetration value', min_value=0, value=1, help='Provide the ap value as a positive number i.e. AP -1 becomes 1')
damage = st.sidebar.number_input("Damage value", min_value=0, max_value=10, value=1)

st.sidebar.subheader("Rerolls")
hit_rr_1 = st.sidebar.checkbox("Reroll ones to hit")
hit_rr_all = st.sidebar.checkbox("Reroll all to hit")
wound_rr_1 = st.sidebar.checkbox("Reroll ones to wound")
wound_rr_all = st.sidebar.checkbox("Reroll all to wound")
exploding_6 = st.sidebar.checkbox("Exploding 6s (inactive)")
exploding_5 = st.sidebar.checkbox("Exploding 5s (inactive)")


if hit_rr_1 == True and hit_rr_all == True:
    st.sidebar.write("Error: you've selected more than 1 hit reroll option")

if wound_rr_1 == True and wound_rr_all == True:
    st.sidebar.write("Error: you've selected more than 1 wound reroll option")

st.sidebar.subheader("Defender values")
defender_name = st.sidebar.text_input("Unit name of the defender", "Defender")
defender_models = st.sidebar.number_input("Number of target models", min_value=1, value=10, step=1)
toughness = st.sidebar.number_input("Toughness value", min_value=1, max_value=15, value=1)
wounds = st.sidebar.number_input("Wounds value", min_value=1, max_value=25, value=1)
save = st.sidebar.slider("(Invul)save value", min_value=2, max_value=6, value=4, step=1)
fnp = st.sidebar.slider("Feel No Pain value", min_value=0, max_value=6, value=0, step=1)


# transform input to probability
hitp = hit_probability(hit_roll, hit_rr_1, hit_rr_all)
missp = 1 - hitp

total_attacks = attacks * attacker_models
total_damage = total_attacks * damage
woundp = wound_roll(strength, toughness, wound_rr_1, wound_rr_all)

savep = save_chance(save, ap)
fnpp = feel_no_pain(fnp)

succesp = hitp * woundp * savep * fnpp
failp = 1 - succesp


total_wounds = defender_models * wounds


# create dataframe
st.write("Probability Chart")
    




# Theory:
# The probability of x scores in y attempts
# P(exactly x scores in y atempts) = (a ** x)(b ** y) * combinations
# x scores need to be adjusted for damage
# y is total expected fails
# x is total expeceted successes



# combinations theory:
    # Find the total number of possibilities to choose k things from n items
    # python code: math.comb(n, k)
    # n = wanted successes
    # k = total dice throws
    

    
data = list(range(0,total_attacks))
df_probability = pd.DataFrame(data, columns=["expected_successes"])

df_probability['min_damage'] = df_probability.expected_successes * damage

df_probability['combinations'] = df_probability.apply(lambda row: comb(total_attacks, row['expected_successes'].astype(int)), axis=1)

df_probability['exact'] = (succesp ** df_probability.expected_successes) * (failp ** (total_attacks - df_probability.expected_successes)) * df_probability.combinations
df_probability['exact_cumsum'] = df_probability.exact.cumsum()
df_probability['atleast'] = (1 - df_probability.exact_cumsum + df_probability.exact)
df_probability['damage_output'] = df_probability.expected_successes * damage
df_probability['wounds'] = total_wounds
    

with header:
    st.title("Warhammer 40.000 Probability Visualisations")
    st.text("We don't hate we calculate, and then, we roll dice. This web application is best viewed in dark mode.")

with metrics:
    st.header("General Probability Metrics")
    
    column_1, column_2, column_3 = st.columns(3)
    
    
    with column_1:
        st.metric(label='AVG DMG output', value=round(succesp * total_damage,1))
        
        
    with column_2:
        
        
        df_filtered = df_probability[df_probability.min_damage == total_wounds]
        kill_chance = df_filtered.atleast.iloc[0]
        
        
        st.metric(label='Probability of kill', value="{}%".format(round(kill_chance * 100,1)))
        
    with column_3:
        st.metric(label='Metric TBD', value=0)
    

with visualisations: 
    st.header("Probability Chart")
    
    
    # set x axis range
    slider_range = st.slider("Select chart range", value=[0,30])
    min_x = slider_range[0]
    max_x = slider_range[1]
    
    
    # plot chart
    x1 = df_probability.damage_output
    y = df_probability.atleast
    x2 = df_probability.wounds
        
    fig1, ax = plt.subplots()
        
    ax.plot(x1, y, color='deepskyblue', linewidth=2, linestyle='-')
    ax.plot(x2, y, color='red', linewidth=2, linestyle=':')
    
    fig_name = "{} {} vs {} {}".format(attacker_models, attacker_name, defender_models, defender_name)
        
        
    # fig layout
    fig1.patch.set_facecolor('#0e1117') # background area around plot
    ax.set_facecolor('#0e1117') # plot background
    ax.tick_params(labelcolor='white')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    # format gridlines
    ax.yaxis.grid(color='lightgrey', linestyle='--', linewidth=0.5)
    
    # set minor tickers
    ax.xaxis.set_minor_locator(MultipleLocator(damage)) # set minor ticks as multiple of 1 'MultipleLocator(1)'
    
    # format tick numbers
    ax.tick_params(axis='both', which='major', labelsize=8, color='white')
    ax.tick_params(axis='both', which='minor', labelsize=6, color='white')
    # ax.tick_params(axis='x', which='minor', bottom=False)
    
    # format axis limit 
    ax.set_ylim([0, 1])
    ax.set_xlim([min_x,max_x])
    
 
    
    # set fig size
    fig1.set_size_inches(15, 4)
    
    # white gridlines
    ax.tick_params(color='white')

    st.pyplot(fig=fig1)
    




    

import os, shutil

run_mdp = """; we'll use the sd integrator (an accurate and efficient leap-frog stochastic dynamics integrator) with 100000 time steps (200ps)
integrator               = sd
nsteps                   = 1250000
dt                       = 0.002
nstenergy                = 1000
nstcalcenergy            = 100 ; should be a divisor of nstdhdl
nstlog                   = 5000
; cut-offs at 1.0nm
rlist                    = 1.1
rvdw                     = 1.1
; Coulomb interactions
coulombtype              = pme
rcoulomb                 = 1.1
fourierspacing           = 0.13
; Constraints
constraints              = h-bonds
; set temperature to 300K
tc-grps                  = system
tau-t                    = 2.0
ref-t                    = 300
; set pressure to 1 bar with a thermostat that gives a correct
; thermodynamic ensemble
pcoupl                   = C-rescale
ref-p                    = 1.0
compressibility          = 4.5e-5
tau-p                    = 5.0

; and set the free energy parameters
free-energy              = yes
couple-moltype           = ethanol
nstdhdl                  = 0 ; frequency for writing energy difference in dhdl.xvg, 0 means no ouput, should be a multiple of nstcalcenergy.
; these 'soft-core' parameters make sure we never get overlapping
; charges as lambda goes to 0
; soft-core function
sc-power                 = 1
sc-sigma                 = 0.3
sc-alpha                 = 1.0
; we still want the molecule to interact with itself at lambda=0
couple-intramol          = no
couple-lambda1           = vdwq
couple-lambda0           = none
init-lambda-state        = {}
; These are the lambda states at which we simulate
; for separate LJ and Coulomb decoupling, use
fep-lambdas              = 0.00 0.05 0.10 0.15 0.20 0.25 0.30 0.35 0.40 0.45 0.50 0.55 0.60 0.65 0.70 0.75 0.80 0.85 0.90 0.95 1.00
"""

number_of_lambdas = 21
for lambda_number in range(number_of_lambdas):
    lambda_directory = os.path.join(output_files, "lambda_{:0>2}".format(lambda_number))
    os.mkdir(lambda_directory)
    gro_file = os.path.join(output_files, "equil.gro")
    top_file = os.path.join(output_files, "topol.top")
    shutil.copy(gro_file, os.path.join(lambda_directory, "conf.gro"))
    shutil.copy(top_file, lambda_directory)
    write_mdp(run_mdp.format(lambda_number), "grompp.mdp", lambda_directory)

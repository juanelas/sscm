import numpy as np

simulations_parameters = [
    # {
    #     # Infection parameters. For the slices with different values of lambda
    #     "mu": 0.05,
    #     # from 0.2 to 3.0 every 0.2. I use 3.1 because final value is not included
    #     "lambdas": np.arange(0.2, 3.1, .3),
    #     "rho0s_per_lambda_delta": {
    #         0: [.01],
    #         0.8: [.01],
    #         2.5: [.01, .4]
    #     },
    #     # the rhos to simulate for specific lambda and lambda_delta
    #     "rhos_over_time": {
    #         "rho_0s": np.arange(.005, 1, .1),
    #         "lambda": None,  # If not set is automatically chosen
    #         "lambda_delta": None  # If not set is automatically chosen
    #     }
    # },
    # {  # Experiment 1
    #     "tag": "ex1",
    #     "mu": 0.5,
    #     "betas": np.array([.01]),
    #     "rho0s_per_beta_delta": {
    #         0.03333333333333333: [.2, .8]
    #     },
    #     "sigma": 0.003322259136212625,
    #     "sigma_delta": 0.01107419712070875
    # },
    # {  # Experiment 1 no stochastic
    #     "tag": "ex1_sigma0",
    #     "mu": 0.5,
    #     "betas": np.array([.01]),
    #     "rho0s_per_beta_delta": {
    #         0.03333333333333333: [.2, .8]
    #     }
    # },
    # {  # Experiment 2
    #     "tag": "ex2",
    #     "mu": 0.970873786407767,
    #     "betas": np.array([0.05]),
    #     "rho0s_per_beta_delta": {
    #         0.16666666666666666: [.2, .8]
    #     },
    #     "sigma": 0.023809523809523808,
    #     "sigma_delta": 0.07936507936507936
    # },
    # {  # Experiment 2 no stochastic
    #     "tag": "ex2_sigma0",
    #     "mu": 0.970873786407767,
    #     "betas": np.array([0.05]),
    #     "rho0s_per_beta_delta": {
    #         0.16666666666666666: [.2, .8]
    #     }
    # },
    # {  # Experiment 3
    #     "tag": "ex3",
    #     "mu": 0.5,
    #     "betas": np.array([.03]),
    #     "rho0s_per_beta_delta": {
    #         0.09999999999999999: [.2, .8]
    #     },
    #     "sigma": 0.009966777408637875,
    #     "sigma_delta": 0.03322259136212625
    # },
    # {  # Experiment 3 no stochastic
    #     "tag": "ex3_sigma0",
    #     "mu": 0.5,
    #     "betas": np.array([.03]),
    #     "rho0s_per_beta_delta": {
    #         0.09999999999999999: [.2, .8]
    #     }
    # }
    {  # Experiment 1 paper
        "tag": "ex1",
        "mu": 0.7,
        "betas": np.array([0.025]),
        "rho0s_per_beta_delta": {
            0.041666666666666664: [.2, .8]
        },
        "timesteps": 2000,
        "sigma": 0.017499999999999998,
        "sigma_delta": 0.041666666666666664,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Experiment 1 paper no stochastic
        "tag": "ex1_sigma0",
        "mu": 0.7,
        "betas": np.array([0.025]),
        "rho0s_per_beta_delta": {
            0.041666666666666664: [.2, .8]
        },
        "timesteps": 2000
    },
    {  # Experiment 2 paper
        "tag": "ex2",
        "mu": 0.5,
        "betas": np.array([0.03]),
        "rho0s_per_beta_delta": {
            0.09999999999999999: [.2, .8]
        },
        "timesteps": 30000,
        "sigma": 0.034999999999999996,
        "sigma_delta": 0.11666666666666665,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Experiment 2 paper no stochastic
        "tag": "ex2_sigma0",
        "mu": 0.5,
        "betas": np.array([0.03]),
        "rho0s_per_beta_delta": {
            0.09999999999999999: [.2, .8]
        },
        "timesteps": 30000
    },
    {  # Experiment 3 paper
        "tag": "ex3",
        "mu": 0.7,
        "betas": np.array([.04]),
        "rho0s_per_beta_delta": {
            0.13333333333333333: [.2, .8]
        },
        "timesteps": 2000,
        "sigma": 0.01,
        "sigma_delta": 0.03333333333333333,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Experiment 3 no paper stochastic
        "tag": "ex3_sigma0",
        "mu": 0.7,
        "betas": np.array([.04]),
        "rho0s_per_beta_delta": {
            0.13333333333333333: [.2, .8]
        },
        "timesteps": 2000,
    },
    {  # Juan's ex1
        "tag": "ex1b",
        "mu": 0.7,
        "betas": np.array([0.013999999999999999]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 2000,
        "sigma": 0.01870828693386971,
        "sigma_delta": 0.009354143466934854,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Juan's ex1
        "tag": "ex1b_sigma0",
        "mu": 0.7,
        "betas": np.array([0.013999999999999999]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 2000
    },
    {  # Juan's ex2
        "tag": "ex2b",
        "mu": 0.5,
        "betas": np.array([0.03]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 20000,
        "sigma": 0.035355339059327376,
        "sigma_delta": 0.017677669529663688,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Juan's ex2
        "tag": "ex2b_sigma0",
        "mu": 0.5,
        "betas": np.array([0.03]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 20000
    },
    {  # Juan's ex3
        "tag": "ex3b",
        "mu": 0.5,
        "betas": np.array([0.0375]),
        "rho0s_per_beta_delta": {
            0.08: [.2, .8]
        },
        "timesteps": 2000,
        "sigma": 0.02738612787525831,
        "sigma_delta": 0.013693063937629155,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Juan's ex3
        "tag": "ex3b_sigma0",
        "mu": 0.5,
        "betas": np.array([0.0375]),
        "rho0s_per_beta_delta": {
            0.08: [.2, .8]
        },
        "timesteps": 2000
    },
    {  # Juan's ex2 InVS15
        "tag": "ex2c",
        "mu": 0.6,
        "betas": np.array([0.03193514708591783]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 2000,
        "sigma": 0.03474086009637279,
        "sigma_delta": 0.017370430048186395,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Juan's ex2 InVS15
        "tag": "ex2c_sigma0",
        "mu": 0.6,
        "betas": np.array([0.03193514708591783]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 2000
    },
	{
		"tag": "J_contact-high-school_ex1",
		"mu": 1,
		"betas": np.array([0.007306578377449296]),
		"rho0s_per_beta_delta": {
			0.2758389873417721: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.0056204881402543835,
		"sigma_delta": 0.2121854686126602,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_contact-high-school_ex1_sigma0",
		"mu": 1,
		"betas": np.array([0.007306578377449296]),
		"rho0s_per_beta_delta": {
			0.2758389873417721: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_contact-high-school_ex2a",
		"mu": 1,
		"betas": np.array([0.02680871674114816]),
		"rho0s_per_beta_delta": {
			0.09772001772151896: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.011522000687521485,
		"sigma_delta": 0.041998657460682765,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_contact-high-school_ex2a_sigma0",
		"mu": 1,
		"betas": np.array([0.02680871674114816]),
		"rho0s_per_beta_delta": {
			0.09772001772151896: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_contact-high-school_ex2b",
		"mu": 1,
		"betas": np.array([0.025224750773461674]),
		"rho0s_per_beta_delta": {
			0.09194632911392403: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.0056204881402543835,
		"sigma_delta": 0.02048714998082086,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_contact-high-school_ex2b_sigma0",
		"mu": 1,
		"betas": np.array([0.025224750773461674]),
		"rho0s_per_beta_delta": {
			0.09194632911392403: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_contact-high-school_ex3",
		"mu": 0.5,
		"betas": np.array([0.017535922997593677]),
		"rho0s_per_beta_delta": {
			0.02869873417721519: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.0056204881402543835,
		"sigma_delta": 0.009198312236286919,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_contact-high-school_ex3_sigma0",
		"mu": 0.5,
		"betas": np.array([0.017535922997593677]),
		"rho0s_per_beta_delta": {
			0.02869873417721519: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_contact-primary-school_ex1",
		"mu": 1,
		"betas": np.array([0.003782584826259469]),
		"rho0s_per_beta_delta": {
			0.09414407472270869: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.002909703017915114,
		"sigma_delta": 0.07241907608728428,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_contact-primary-school_ex1_sigma0",
		"mu": 1,
		"betas": np.array([0.003782584826259469]),
		"rho0s_per_beta_delta": {
			0.09414407472270869: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_contact-primary-school_ex2a",
		"mu": 1,
		"betas": np.array([0.013878759648911868]),
		"rho0s_per_beta_delta": {
			0.033351922942206645: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.005964891186725983,
		"sigma_delta": 0.01433417655834468,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_contact-primary-school_ex2a_sigma0",
		"mu": 1,
		"betas": np.array([0.013878759648911868]),
		"rho0s_per_beta_delta": {
			0.033351922942206645: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_contact-primary-school_ex2b",
		"mu": 1,
		"betas": np.array([0.013058747144403032]),
		"rho0s_per_beta_delta": {
			0.03138135824090289: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.002909703017915114,
		"sigma_delta": 0.006992281247973016,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_contact-primary-school_ex2b_sigma0",
		"mu": 1,
		"betas": np.array([0.013058747144403032]),
		"rho0s_per_beta_delta": {
			0.03138135824090289: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_contact-primary-school_ex3",
		"mu": 0.5,
		"betas": np.array([0.009078273415895155]),
		"rho0s_per_beta_delta": {
			0.009794901731854445: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.002909703017915114,
		"sigma_delta": 0.003139391580722579,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_contact-primary-school_ex3_sigma0",
		"mu": 0.5,
		"betas": np.array([0.009078273415895155]),
		"rho0s_per_beta_delta": {
			0.009794901731854445: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_email-Eu_ex1",
		"mu": 1,
		"betas": np.array([0.004428103416498856]),
		"rho0s_per_beta_delta": {
			0.012423035397403566: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.003406259599303731,
		"sigma_delta": 0.009556254584576472,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_email-Eu_ex1_sigma0",
		"mu": 1,
		"betas": np.array([0.004428103416498856]),
		"rho0s_per_beta_delta": {
			0.012423035397403566: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_email-Eu_ex1b",
		"mu": 1,
		"betas": np.array([0.008595730161438957]),
		"rho0s_per_beta_delta": {
			0.02411530400672457: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.023843817195126113,
		"sigma_delta": 0.0668937820920353,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_email-Eu_ex1b_sigma0",
		"mu": 1,
		"betas": np.array([0.008595730161438957]),
		"rho0s_per_beta_delta": {
			0.02411530400672457: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_email-Eu_ex2a",
		"mu": 1,
		"betas": np.array([0.01624724516195092]),
		"rho0s_per_beta_delta": {
			0.004401042981227234: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.006982832178572647,
		"sigma_delta": 0.0018915049439005725,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_email-Eu_ex2a_sigma0",
		"mu": 1,
		"betas": np.array([0.01624724516195092]),
		"rho0s_per_beta_delta": {
			0.004401042981227234: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_email-Eu_ex2b",
		"mu": 1,
		"betas": np.array([0.015287293081675143]),
		"rho0s_per_beta_delta": {
			0.0041410117991345224: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.003406259599303731,
		"sigma_delta": 0.0009226853384880844,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_email-Eu_ex2b_sigma0",
		"mu": 1,
		"betas": np.array([0.015287293081675143]),
		"rho0s_per_beta_delta": {
			0.0041410117991345224: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_email-Eu_ex3",
		"mu": 0.5,
		"betas": np.array([0.010627529949827639]),
		"rho0s_per_beta_delta": {
			0.0012925126864045328: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.003406259599303731,
		"sigma_delta": 0.00041426688666811956,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_email-Eu_ex3_sigma0",
		"mu": 0.5,
		"betas": np.array([0.010627529949827639]),
		"rho0s_per_beta_delta": {
			0.0012925126864045328: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_NDC-classes_ex1",
		"mu": 1,
		"betas": np.array([0.024257286885245904]),
		"rho0s_per_beta_delta": {
			0.07373864091241224: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.0186595949855352,
		"sigma_delta": 0.05672246779776171,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_NDC-classes_ex1_sigma0",
		"mu": 1,
		"betas": np.array([0.024257286885245904]),
		"rho0s_per_beta_delta": {
			0.07373864091241224: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_NDC-classes_ex2a",
		"mu": 1,
		"betas": np.array([0.0890029093539055]),
		"rho0s_per_beta_delta": {
			0.02612299793500016: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.03825216972034715,
		"sigma_delta": 0.01122728861188689,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_NDC-classes_ex2a_sigma0",
		"mu": 1,
		"betas": np.array([0.0890029093539055]),
		"rho0s_per_beta_delta": {
			0.02612299793500016: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_NDC-classes_ex2b",
		"mu": 1,
		"betas": np.array([0.08374426229508197]),
		"rho0s_per_beta_delta": {
			0.02457954697080408: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.0186595949855352,
		"sigma_delta": 0.005476726152139948,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_NDC-classes_ex2b_sigma0",
		"mu": 1,
		"betas": np.array([0.08374426229508197]),
		"rho0s_per_beta_delta": {
			0.02457954697080408: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_NDC-classes_ex3",
		"mu": 0.5,
		"betas": np.array([0.05821793635486982]),
		"rho0s_per_beta_delta": {
			0.007671887409854816: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.0186595949855352,
		"sigma_delta": 0.0024589382723893645,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_NDC-classes_ex3_sigma0",
		"mu": 0.5,
		"betas": np.array([0.05821793635486982]),
		"rho0s_per_beta_delta": {
			0.007671887409854816: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_tags-ask-ubuntu_ex1",
		"mu": 1,
		"betas": np.array([0.002967280099168821]),
		"rho0s_per_beta_delta": {
			0.02167590820742458: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.002282540711212256,
		"sigma_delta": 0.016673903804971257,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_tags-ask-ubuntu_ex1_sigma0",
		"mu": 1,
		"betas": np.array([0.002967280099168821]),
		"rho0s_per_beta_delta": {
			0.02167590820742458: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_tags-ask-ubuntu_ex2a",
		"mu": 1,
		"betas": np.array([0.010887308335154442]),
		"rho0s_per_beta_delta": {
			0.00767900924583615: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.0046792084579851245,
		"sigma_delta": 0.003300327675669964,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_tags-ask-ubuntu_ex2a_sigma0",
		"mu": 1,
		"betas": np.array([0.010887308335154442]),
		"rho0s_per_beta_delta": {
			0.00767900924583615: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_tags-ask-ubuntu_ex2b",
		"mu": 1,
		"betas": np.array([0.010244042711920606]),
		"rho0s_per_beta_delta": {
			0.007225302735808195: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.002282540711212256,
		"sigma_delta": 0.0016099159393512022,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_tags-ask-ubuntu_ex2b_sigma0",
		"mu": 1,
		"betas": np.array([0.010244042711920606]),
		"rho0s_per_beta_delta": {
			0.007225302735808195: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_tags-ask-ubuntu_ex3",
		"mu": 0.5,
		"betas": np.array([0.007121527018982239]),
		"rho0s_per_beta_delta": {
			0.002255196532185031: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.002282540711212256,
		"sigma_delta": 0.0007228194013413561,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_tags-ask-ubuntu_ex3_sigma0",
		"mu": 0.5,
		"betas": np.array([0.007121527018982239]),
		"rho0s_per_beta_delta": {
			0.002255196532185031: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_InVS15_ex1",
		"mu": 1,
		"betas": np.array([0.01064495480880649]),
		"rho0s_per_beta_delta": {
			0.8667288343558281: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.008188489764387795,
		"sigma_delta": 0.6667196165784568,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_InVS15_ex1_sigma0",
		"mu": 1,
		"betas": np.array([0.01064495480880649]),
		"rho0s_per_beta_delta": {
			0.8667288343558281: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_InVS15_ex1b",
		"mu": 1,
		"betas": np.array([0.020663735805330243]),
		"rho0s_per_beta_delta": {
			1.6824736196319015: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.05731942835071456,
		"sigma_delta": 4.667037316049197,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_InVS15_ex1b_sigma0",
		"mu": 1,
		"betas": np.array([0.020663735805330243]),
		"rho0s_per_beta_delta": {
			1.6824736196319015: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_InVS15_ex2a",
		"mu": 1,
		"betas": np.array([0.03905762224797219]),
		"rho0s_per_beta_delta": {
			0.30705143558282205: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.01678640401699498,
		"sigma_delta": 0.1319662886534052,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_InVS15_ex2a_sigma0",
		"mu": 1,
		"betas": np.array([0.03905762224797219]),
		"rho0s_per_beta_delta": {
			0.30705143558282205: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_InVS15_ex2b",
		"mu": 1,
		"betas": np.array([0.03674994206257243]),
		"rho0s_per_beta_delta": {
			0.2889096114519427: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.008188489764387795,
		"sigma_delta": 0.06437379934312448,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_InVS15_ex2b_sigma0",
		"mu": 1,
		"betas": np.array([0.03674994206257243]),
		"rho0s_per_beta_delta": {
			0.2889096114519427: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_InVS15_ex2c",
		"mu": 1,
		"betas": np.array([0.03331548474314407]),
		"rho0s_per_beta_delta": {
			1.0079321063394684: [0.01, 0.2]
		},
		"timesteps": 48000,
		"sigma": 0.023337195828505214,
		"sigma_delta": 0.7060473269062225,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_InVS15_ex2c_sigma0",
		"mu": 1,
		"betas": np.array([0.03331548474314407]),
		"rho0s_per_beta_delta": {
			1.0079321063394684: [0.01, 0.2]
		},
		"timesteps": 48000
	},
	{
		"tag": "J_InVS15_ex3",
		"mu": 0.5,
		"betas": np.array([0.02554808806488992]),
		"rho0s_per_beta_delta": {
			0.0901758691206544: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.008188489764387795,
		"sigma_delta": 0.028902522154055896,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_InVS15_ex3_sigma0",
		"mu": 0.5,
		"betas": np.array([0.02554808806488992]),
		"rho0s_per_beta_delta": {
			0.0901758691206544: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_InVS15_ex3b",
		"mu": 0.5,
		"betas": np.array([0.04446349942062573]),
		"rho0s_per_beta_delta": {
			0.15694069529652355: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.036848203939745076,
		"sigma_delta": 0.13006134969325153,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_InVS15_ex3b_sigma0",
		"mu": 0.5,
		"betas": np.array([0.04446349942062573]),
		"rho0s_per_beta_delta": {
			0.15694069529652355: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_N500_k499.000_kdelta483.234_ex1",
		"mu": 1,
		"betas": np.array([0.0005210380761523047]),
		"rho0s_per_beta_delta": {
			0.01241137833844473: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.0004008016032064128,
		"sigma_delta": 0.009547287547169384,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_N500_k499.000_kdelta483.234_ex1_sigma0",
		"mu": 1,
		"betas": np.array([0.0005210380761523047]),
		"rho0s_per_beta_delta": {
			0.01241137833844473: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	},
	{
		"tag": "J_N500_k499.000_kdelta483.234_ex2a",
		"mu": 1,
		"betas": np.array([0.0019117515030060118]),
		"rho0s_per_beta_delta": {
			0.004396913296663728: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.0008216432865731462,
		"sigma_delta": 0.0018897300648998583,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_N500_k499.000_kdelta483.234_ex2a_sigma0",
		"mu": 1,
		"betas": np.array([0.0019117515030060118]),
		"rho0s_per_beta_delta": {
			0.004396913296663728: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_N500_k499.000_kdelta483.234_ex2b",
		"mu": 1,
		"betas": np.array([0.001798797595190381]),
		"rho0s_per_beta_delta": {
			0.00413712611281491: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000,
		"sigma": 0.0004008016032064128,
		"sigma_delta": 0.0009218195438535895,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_N500_k499.000_kdelta483.234_ex2b_sigma0",
		"mu": 1,
		"betas": np.array([0.001798797595190381]),
		"rho0s_per_beta_delta": {
			0.00413712611281491: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 4000
	},
	{
		"tag": "J_N500_k499.000_kdelta483.234_ex3",
		"mu": 0.5,
		"betas": np.array([0.001250501002004008]),
		"rho0s_per_beta_delta": {
			0.00129129986714511: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000,
		"sigma": 0.0004008016032064128,
		"sigma_delta": 0.0004138781625465096,
		"bounded_delta": False,
		"independent_noises": False
	},
	{
		"tag": "J_N500_k499.000_kdelta483.234_ex3_sigma0",
		"mu": 0.5,
		"betas": np.array([0.001250501002004008]),
		"rho0s_per_beta_delta": {
			0.00129129986714511: [0.01, 0.04, 0.2, 0.6]
		},
		"timesteps": 1000
	}
]

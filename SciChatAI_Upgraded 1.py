"""
SciChatAI — Educational Science Chatbot
Copyright (c) 2026 SciChatAI

Requirements: Python 3.8 or newer.
Uses only Python's standard library.

Local testing:
http://127.0.0.1:8000

Public deployment:
Deploy this application to a hosting service such as Render
to make it accessible through a public URL.

Server:
Keeps running until you press Ctrl+C in the terminal
or the hosting platform stops the application.
"""

import json
import os
import re
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


APP_NAME = "SciChatAI"
HOST = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
PORT = int(os.environ.get("PORT", "8000"))

LEADERSHIP = {
    "Legal Advisor": "PARKSHITH K NAIK",
    "Chairperson": "PRATIBHA VENKATESH",
    "Founder": "JEEVAN RATHOD V",
}

FOUNDER_PROFILE = """
Jeevan Rathod V is presented in the profile supplied for this SciChatAI
project as an independent young researcher from Davanagere, Karnataka, India.

His stated interests include theoretical physics, cosmology, astrophysics,
the cosmological constant, and the vacuum catastrophe.

His proposed concepts include Infinite Rathod's Particles (R-P) and the
White Paper Cosmos Hypothesis. These should be understood as proposed
ideas or hypotheses, not established scientific discoveries. Independent
scientific review and experimental evidence are needed to validate new
theories.

Portfolio:
https://sites.google.com/view/davangeresyoungestresearcherin

LinkedIn:
https://in.linkedin.com/in/jeevan-rathod-v-b471493ba

YouTube:
https://www.youtube.com/@jeevanrathodv

ORCID:
https://orcid.org/0009-0001-4317-003X
"""


# Each topic has a title, category, searchable keywords, and an answer.
# The question bank combines these topics with 20 question templates.
TOPICS = [
    {
        "title": "General Science",
        "category": "General Science",
        "keywords": ["science", "scientific method", "experiment",
                     "observation", "hypothesis", "evidence"],
        "answer": """
Science is a systematic way of understanding the natural world through
observation, measurement, experiments, and evidence. Scientists begin
with questions, develop hypotheses, test predictions, analyse results,
and communicate their findings.

The scientific method is not always a perfectly straight line. New
evidence can lead scientists to revise an explanation or design a
different experiment. Reproducibility, peer review, and careful
measurement help make scientific conclusions more reliable.

Science is used in medicine, engineering, agriculture, computing,
environmental protection, and everyday decision-making. A good
scientific explanation must be consistent with evidence and open to
testing.
"""
    },
    {
        "title": "Physics",
        "category": "Physics",
        "keywords": ["physics", "force", "motion", "energy", "matter",
                     "newton", "mechanics"],
        "answer": """
Physics studies matter, energy, motion, forces, space, and time.
Classical mechanics describes many everyday movements, while
electromagnetism explains electric and magnetic phenomena. Thermodynamics
studies heat and energy transfer, and modern physics includes quantum
mechanics and relativity.

Newton's laws explain how forces affect motion. Energy can be transferred
between objects and transformed from one form into another. Physics
supports technologies such as electric motors, medical imaging,
communication systems, renewable energy, and spacecraft.

Scientific models have limits: the most useful model depends on the
scale and conditions of the problem being studied.
"""
    },
    {
        "title": "Chemistry",
        "category": "Chemistry",
        "keywords": ["chemistry", "atom", "molecule", "element",
                     "compound", "reaction", "chemical"],
        "answer": """
Chemistry studies the composition, structure, properties, and changes
of matter. Atoms contain protons and neutrons in a nucleus, with
electrons occupying surrounding regions. Elements are defined by their
number of protons, while compounds contain elements chemically combined
in particular proportions.

Chemical reactions rearrange atoms and form new substances. Bonds,
energy changes, temperature, concentration, and catalysts can affect
reaction rates. The periodic table organises elements by atomic number
and recurring chemical properties.

Chemistry helps explain medicines, batteries, food, materials,
agriculture, water treatment, and environmental processes. Safe
laboratory practice is essential when working with chemicals.
"""
    },
    {
        "title": "Biology",
        "category": "Biology",
        "keywords": ["biology", "life", "organism", "cell", "living",
                     "organ", "tissue"],
        "answer": """
Biology is the scientific study of living organisms and their
interactions with the environment. Living systems commonly involve
cells, genetic information, metabolism, growth, and reproduction.
Viruses have some life-like characteristics but depend on host cells
to reproduce, so their classification as living entities is debated.

Biology includes genetics, ecology, evolution, microbiology, physiology,
and molecular biology. Cells use DNA to store hereditary information,
while proteins perform many structural and chemical functions.

Biological research supports healthcare, conservation, food production,
biotechnology, and our understanding of ecosystems.
"""
    },
    {
        "title": "Mathematics",
        "category": "Mathematics",
        "keywords": ["mathematics", "math", "algebra", "geometry",
                     "equation", "number", "calculation"],
        "answer": """
Mathematics studies numbers, patterns, structures, quantities, and
logical relationships. Arithmetic handles basic numerical operations;
algebra uses symbols to express relationships; geometry studies shapes
and space; and statistics helps analyse data.

An equation states that two expressions have equal values. Solving an
equation means finding values that satisfy it. Mathematical reasoning
depends on clearly stated assumptions and valid logical steps.

Mathematics is essential in physics, engineering, finance, computer
science, medicine, architecture, and data analysis. Showing each step
of a solution makes mistakes easier to find and results easier to verify.
"""
    },
    {
        "title": "Astronomy",
        "category": "Astronomy",
        "keywords": ["astronomy", "star", "planet", "moon", "galaxy",
                     "telescope", "solar system"],
        "answer": """
Astronomy studies objects and phenomena beyond Earth's atmosphere,
including planets, moons, stars, nebulae, galaxies, and the universe
as a whole. Astronomers use telescopes, spacecraft, spectroscopy,
mathematics, and computer models to study these objects.

The Solar System contains the Sun, eight recognised planets, dwarf
planets, moons, asteroids, and comets. Stars produce energy mainly
through nuclear fusion in their cores. Galaxies contain stars, gas,
dust, and dark matter.

Because light takes time to travel, observing distant objects also
allows astronomers to study earlier stages of cosmic history.
"""
    },
    {
        "title": "Earth Science",
        "category": "Earth Science",
        "keywords": ["earth science", "geology", "rock", "mineral",
                     "tectonic", "earthquake", "volcano"],
        "answer": """
Earth science studies our planet's structure, materials, atmosphere,
oceans, and history. Geology examines rocks, minerals, fossils, and
processes within Earth's crust. Plate tectonics explains the movement
of large sections of the lithosphere and helps account for many
earthquakes, volcanoes, and mountain ranges.

Earth's interior includes the crust, mantle, liquid outer core, and
solid inner core. Geological evidence comes from field observations,
laboratory measurements, seismic waves, satellites, and drilling.

Earth science helps people understand natural hazards, locate resources,
study groundwater, and reconstruct the planet's long history.
"""
    },
    {
        "title": "Environmental Science",
        "category": "Environment",
        "keywords": ["environment", "pollution", "climate change",
                     "ecosystem", "conservation", "sustainability"],
        "answer": """
Environmental science examines interactions between natural systems
and human activities. It combines biology, chemistry, geology,
climatology, economics, and social science to investigate issues such
as pollution, biodiversity loss, resource use, and climate change.

Climate change refers to long-term changes in temperatures and weather
patterns. Human greenhouse-gas emissions are the main driver of the
rapid global warming observed since the industrial era. Impacts vary
by region and include rising sea levels, heat extremes, and changes
in precipitation.

Solutions include cleaner energy, efficiency, ecosystem protection,
adaptation planning, reduced waste, and evidence-based public policy.
"""
    },
    {
        "title": "Computer Science",
        "category": "Computer Science",
        "keywords": ["computer science", "computer", "algorithm",
                     "programming", "software", "code", "python"],
        "answer": """
Computer science studies computation, algorithms, data, programming
languages, and computer systems. An algorithm is a finite sequence
of instructions for solving a problem. A program implements instructions
in a language that a computer can execute or interpret.

Python is a widely used programming language because its syntax is
readable and its standard library supports many tasks. Programs should
be tested with normal inputs, unusual inputs, and error cases.

Computer science supports web applications, scientific simulations,
robotics, cybersecurity, data analysis, artificial intelligence,
education, and many other fields.
"""
    },
    {
        "title": "Artificial Intelligence",
        "category": "Computer Science",
        "keywords": ["artificial intelligence", "ai", "machine learning",
                     "chatbot", "neural network", "language model"],
        "answer": """
Artificial intelligence (AI) is a field of computing concerned with
systems that perform tasks such as recognising patterns, processing
language, making predictions, or planning actions.

Machine learning is a branch of AI in which models learn patterns from
data. A chatbot can use fixed rules, a knowledge base, a trained
language model, or a combination of approaches. These methods have
different strengths and limitations.

AI systems can produce errors, reflect biases in their data, or present
uncertain information confidently. Important results should be checked
against reliable sources. SciChatAI's current built-in mode uses
topic matching and prepared educational explanations; it is not a
live, internet-connected general-purpose AI model.
"""
    },
    {
        "title": "Human Body",
        "category": "Biology",
        "keywords": ["human body", "heart", "brain", "lung", "blood",
                     "organ system", "anatomy"],
        "answer": """
The human body contains specialised cells organised into tissues,
organs, and organ systems. The circulatory system transports blood;
the respiratory system exchanges oxygen and carbon dioxide; the
nervous system processes information; and the digestive system breaks
food down so nutrients can be absorbed.

The brain and spinal cord form the central nervous system. The heart
pumps blood through blood vessels, and the lungs exchange gases with
the environment. These systems interact to maintain homeostasis,
which is the regulation of internal conditions.

Human biology is complex, and this general explanation is educational
rather than a substitute for personalised medical advice.
"""
    },
    {
        "title": "Genetics and DNA",
        "category": "Biology",
        "keywords": ["genetics", "dna", "gene", "chromosome",
                     "heredity", "mutation", "rna"],
        "answer": """
Genetics studies heredity and variation. DNA stores biological
information in a sequence of chemical bases. A gene is a region of
DNA associated with a functional product, often a protein or RNA.
Genes are organised on chromosomes in cells.

When cells divide, DNA is copied. Mutations are changes in genetic
sequence; their effects can be neutral, harmful, or occasionally
beneficial in a particular environment. Traits usually reflect
interactions among genes, development, and environmental influences.

Genetics is important in evolution, agriculture, medicine, ancestry
research, and biotechnology. Genetic findings require careful
interpretation because inheritance is often more complex than a
single gene determining a single trait.
"""
    },
    {
        "title": "Evolution",
        "category": "Biology",
        "keywords": ["evolution", "natural selection", "adaptation",
                     "species", "fossil", "natural history"],
        "answer": """
Evolution is change in inherited characteristics of populations
across generations. Mechanisms include natural selection, mutation,
genetic drift, and gene flow. Natural selection occurs when heritable
differences affect survival or reproduction in a particular environment.

Evidence for evolution includes fossils, comparative anatomy, observed
changes in populations, biogeography, and similarities in DNA.
Adaptations develop across generations; individual organisms do not
evolve genetically simply because they need a trait.

Evolutionary biology explains the diversity and relationships of life
and contributes to medicine, agriculture, ecology, and conservation.
"""
    },
    {
        "title": "Electricity",
        "category": "Physics",
        "keywords": ["electricity", "electric current", "voltage",
                     "resistance", "circuit", "ohm", "charge"],
        "answer": """
Electricity involves electric charge and its effects. Electric current
is the rate at which charge flows, voltage is electric potential
difference, and resistance describes how strongly a component opposes
current.

For many ohmic components, Ohm's law is V = I × R, where V is voltage,
I is current, and R is resistance. In a simple circuit, a power source,
conducting path, and load work together. Electrical power is commonly
calculated as P = V × I.

Electricity is useful but can be dangerous. Do not experiment with
mains electricity; use safe, low-voltage educational equipment with
appropriate supervision.
"""
    },
    {
        "title": "Magnetism",
        "category": "Physics",
        "keywords": ["magnetism", "magnet", "magnetic field",
                     "electromagnet", "north pole", "south pole"],
        "answer": """
Magnetism is associated with moving electric charges and intrinsic
magnetic properties of particles. A magnet produces a magnetic field,
which can exert forces on other magnets and suitable materials.

Every ordinary bar magnet has north and south poles. Like poles repel
and unlike poles attract. Electric currents can create magnetic fields,
which is the operating principle behind electromagnets, electric
motors, generators, and many sensors.

Electricity and magnetism are unified in electromagnetism. Changing
magnetic fields can induce electric currents, a principle used in
generators and transformers.
"""
    },
    {
        "title": "Light and Optics",
        "category": "Physics",
        "keywords": ["light", "optics", "reflection", "refraction",
                     "lens", "spectrum", "wavelength"],
        "answer": """
Light is electromagnetic radiation visible to the human eye.
It can be described using waves and, in quantum physics, photons.
Its behaviour includes reflection, refraction, diffraction, and
interference.

Reflection occurs when light bounces from a surface. Refraction is
a change in direction caused by a change in propagation speed between
materials. Lenses use refraction to focus or spread light. A prism
can separate white light into a spectrum of colours.

Optics is important in glasses, cameras, microscopes, telescopes,
fibre-optic communications, lasers, and medical instruments.
"""
    },
    {
        "title": "Sound and Waves",
        "category": "Physics",
        "keywords": ["sound", "wave", "frequency", "amplitude",
                     "pitch", "vibration", "echo"],
        "answer": """
A wave transfers energy from place to place. Mechanical waves, such
as sound, require a medium, while electromagnetic waves can travel
through a vacuum. Sound is produced by vibrations and travels through
materials as pressure disturbances.

Frequency is the number of cycles per second and is measured in hertz.
For sound, frequency is related to perceived pitch, while amplitude
is related to loudness. The speed of sound depends on the medium and
conditions such as temperature.

Waves are important in music, communications, medical ultrasound,
earthquake studies, and many technologies.
"""
    },
    {
        "title": "Thermodynamics",
        "category": "Physics",
        "keywords": ["thermodynamics", "heat", "temperature",
                     "entropy", "thermal energy", "conduction"],
        "answer": """
Thermodynamics studies heat, temperature, work, and energy. Temperature
is related to the average microscopic kinetic energy of particles,
while heat is energy transferred because of a temperature difference.

Heat transfer occurs through conduction, convection, and radiation.
The first law of thermodynamics expresses conservation of energy.
The second law describes the direction of spontaneous processes and
the tendency for total entropy to increase in an isolated system.

Thermodynamics helps explain engines, refrigerators, power plants,
weather, chemical processes, and the thermal behaviour of materials.
"""
    },
    {
        "title": "Quantum Physics",
        "category": "Physics",
        "keywords": ["quantum physics", "quantum mechanics", "electron",
                     "superposition", "uncertainty", "quantum"],
        "answer": """
Quantum mechanics is the framework used to describe matter and
radiation at atomic and subatomic scales. It predicts probabilities
for measurement outcomes and explains phenomena that classical
physics cannot fully describe.

Important concepts include quantised energy levels, wave-particle
duality, superposition, and the uncertainty principle. Quantum theory
has been tested extensively and underpins technologies such as
semiconductors, lasers, atomic clocks, and some medical imaging methods.

Quantum ideas can be counterintuitive, so claims about them should be
evaluated using precise definitions, mathematics, and experimental
evidence rather than science-fiction interpretations.
"""
    },
    {
        "title": "Relativity",
        "category": "Physics",
        "keywords": ["relativity", "einstein", "space time", "gravity",
                     "special relativity", "general relativity"],
        "answer": """
Einstein's theories of relativity changed our understanding of space,
time, motion, and gravity. Special relativity applies to inertial
frames and shows that measurements of time and length depend on
relative motion. It also relates mass and energy through E = mc².

General relativity describes gravity in terms of the curvature of
spacetime associated with matter and energy. Its predictions include
the bending of light, gravitational time dilation, and gravitational
waves, all supported by observations.

Relativity is important for understanding black holes, cosmology,
precision navigation, and high-speed particles.
"""
    },
    {
        "title": "The Solar System",
        "category": "Astronomy",
        "keywords": ["solar system", "sun", "mercury", "venus", "mars",
                     "jupiter", "saturn", "uranus", "neptune"],
        "answer": """
The Solar System formed about 4.6 billion years ago from a cloud of
gas and dust. The Sun contains most of its mass. Eight planets orbit
the Sun: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and
Neptune.

The inner planets are rocky. Jupiter and Saturn are gas giants, while
Uranus and Neptune are ice giants. The system also includes dwarf
planets, moons, asteroids, comets, and dust. Gravity governs the
orbits of these objects.

Space missions and telescopes help scientists compare planetary
atmospheres, surfaces, magnetic fields, and histories.
"""
    },
    {
        "title": "The Universe",
        "category": "Astronomy",
        "keywords": ["universe", "big bang", "cosmos", "cosmology",
                     "expansion", "dark matter", "dark energy"],
        "answer": """
Cosmology studies the universe on its largest scales. The leading
cosmological model describes the universe as evolving from an early
hot, dense state about 13.8 billion years ago. Evidence includes
cosmic expansion, the cosmic microwave background, and the abundance
of light elements.

The universe continues to expand. Observations indicate that its
expansion is accelerating, a phenomenon commonly attributed to dark
energy, whose physical nature remains uncertain. Dark matter is inferred
from gravitational effects and is distinct from ordinary matter.

Open questions in cosmology require careful observation, mathematical
models, and tests against independent evidence.
"""
    },
    {
        "title": "Black Holes",
        "category": "Astronomy",
        "keywords": ["black hole", "event horizon", "singularity",
                     "gravity", "accretion disk"],
        "answer": """
A black hole is a region of spacetime where gravity is so strong that
inside its event horizon, light cannot escape to distant observers.
Black holes can form through the collapse of massive stars, and
supermassive black holes are found in many galaxy centres.

Scientists study black holes by observing their effects on nearby
matter, stars, and light. Accretion disks around some black holes
become extremely hot and emit radiation. Gravitational-wave detectors
have also measured signals from merging black holes.

The event horizon is not a solid surface. Many details of black-hole
interiors remain active topics in theoretical physics.
"""
    },
    {
        "title": "Climate and Weather",
        "category": "Environment",
        "keywords": ["climate", "weather", "greenhouse effect",
                     "rainfall", "temperature", "monsoon"],
        "answer": """
Weather describes short-term atmospheric conditions, such as rain,
wind, temperature, and cloud cover. Climate describes long-term
patterns and statistics, usually assessed over decades.

The natural greenhouse effect keeps Earth warmer than it would be
otherwise. Increasing concentrations of greenhouse gases from human
activities strengthen this effect and cause global warming. Local
weather still varies from day to day, so one cold day does not
contradict a long-term warming trend.

Meteorologists use observations and computer models to forecast
weather, while climate scientists study long-term changes and risks.
"""
    },
    {
        "title": "Oceans",
        "category": "Earth Science",
        "keywords": ["ocean", "sea", "marine", "tide", "coral reef",
                     "ocean current", "salinity"],
        "answer": """
Earth's oceans regulate climate, support biodiversity, transport
heat, and participate in the global carbon cycle. Ocean water contains
dissolved salts, and its density depends partly on temperature and
salinity.

Winds, differences in water density, Earth's rotation, and tides help
drive ocean circulation. Marine ecosystems range from coastal wetlands
and coral reefs to the deep sea. Human pressures include pollution,
overfishing, habitat damage, warming, and ocean acidification.

Ocean research uses ships, buoys, satellites, underwater vehicles,
and long-term monitoring to understand this essential Earth system.
"""
    },
    {
        "title": "Plants and Photosynthesis",
        "category": "Biology",
        "keywords": ["plant", "photosynthesis", "chlorophyll",
                     "carbon dioxide", "glucose", "leaf"],
        "answer": """
Photosynthesis is the process by which plants, algae, and some
bacteria use light energy to build energy-rich organic molecules.
In plants, chlorophyll-containing chloroplasts capture light energy.
Carbon dioxide and water are used to produce sugars, and oxygen is
released in oxygenic photosynthesis.

Photosynthesis supports most food webs and helps move carbon from
the atmosphere into living systems. Plant growth also depends on
water, mineral nutrients, temperature, and other environmental
conditions.

Plants additionally influence soil stability, water cycles, habitats,
agriculture, and the global carbon balance.
"""
    },
    {
        "title": "Microbiology",
        "category": "Biology",
        "keywords": ["microbiology", "bacteria", "virus", "fungus",
                     "microbe", "microorganism"],
        "answer": """
Microbiology studies organisms and biological agents too small to
be seen clearly without suitable instruments. It includes bacteria,
archaea, microscopic fungi, protists, and viruses.

Microorganisms play important roles in digestion, decomposition,
nutrient cycling, food production, and biotechnology. Some cause
infectious diseases, while many are harmless or beneficial. Antibiotics
target certain bacteria and do not treat viral infections; their use
should follow qualified medical guidance.

Microscopes, culturing, molecular tests, and genome analysis help
scientists identify microbes and study their biology.
"""
    },
    {
        "title": "Human Health and Nutrition",
        "category": "Biology",
        "keywords": ["health", "nutrition", "vitamin", "protein",
                     "carbohydrate", "diet", "wellbeing"],
        "answer": """
Nutrition studies how the body obtains and uses energy and nutrients.
Carbohydrates, fats, and proteins provide energy or building materials.
Vitamins and minerals support many essential biological processes,
while water is necessary for transport, temperature regulation, and
normal cell function.

A varied eating pattern, adequate sleep, physical activity, hygiene,
and preventive healthcare support general wellbeing. Nutritional
needs differ by age, activity, health, and other circumstances.

This is general educational information, not a personalised medical
plan. Health concerns should be discussed with a qualified health
professional.
"""
    },
    {
        "title": "Probability and Statistics",
        "category": "Mathematics",
        "keywords": ["probability", "statistics", "data", "average",
                     "mean", "median", "sample"],
        "answer": """
Statistics is the study of collecting, summarising, analysing, and
interpreting data. Probability provides a mathematical framework
for describing uncertainty. The mean is the arithmetic average, the
median is the middle value after sorting, and the mode is the most
frequent value.

A sample should be chosen carefully because biased sampling can
produce misleading conclusions. Correlation indicates association
between variables but does not by itself prove causation. Graphs,
uncertainty estimates, and transparent methods make analyses easier
to interpret.

Statistics is used in science, public health, business, engineering,
and everyday decision-making.
"""
    },
    {
        "title": "Robotics",
        "category": "Technology",
        "keywords": ["robotics", "robot", "sensor", "actuator",
                     "automation", "control system"],
        "answer": """
Robotics combines mechanical engineering, electronics, control
theory, and computer science to build machines that sense and act
in their environments. Sensors collect information, controllers
process it, and actuators produce movement or other actions.

Robots can perform repetitive industrial tasks, assist in surgery,
explore dangerous environments, support agriculture, and investigate
other planets. Reliable robots require testing, safe mechanical
design, robust software, and consideration of human interaction.

Not every robot is autonomous; some are operated directly by people,
while others combine automated behaviour with human supervision.
"""
    },
    {
        "title": "Renewable Energy",
        "category": "Environment",
        "keywords": ["renewable energy", "solar energy", "wind energy",
                     "hydropower", "clean energy", "sustainability"],
        "answer": """
Renewable energy comes from sources replenished naturally on human
timescales, including sunlight, wind, flowing water, geothermal heat,
and sustainably managed biomass. Solar panels convert light into
electricity, while wind turbines convert some of the kinetic energy
of moving air into electrical energy.

Renewable technologies can reduce greenhouse-gas emissions, but
their full environmental impacts depend on manufacturing, land use,
materials, storage, and grid design. Energy storage, transmission,
efficiency, and a diverse energy mix can help balance supply and demand.

Choosing energy technologies requires comparing costs, reliability,
environmental effects, and local conditions.
"""
    },
    {
        "title": "Scientific Research",
        "category": "General Science",
        "keywords": ["research", "peer review", "paper", "citation",
                     "scientific publication", "experiment design"],
        "answer": """
Scientific research begins with a clearly defined question and a
method suited to answering it. Researchers review existing evidence,
state hypotheses or objectives, collect data, document methods, and
analyse uncertainty.

Peer review allows other specialists to critique a manuscript before
publication, but it does not guarantee that every conclusion is
correct. Strong findings are supported by transparent methods,
appropriate data, independent replication where possible, and
consistency with other evidence.

A good research report distinguishes observations from interpretations,
acknowledges limitations, cites sources, and explains what future
work could test.
"""
    },
    {
        "title": "Scientific Units and Measurement",
        "category": "General Science",
        "keywords": ["units", "measurement", "si units", "metre",
                     "kilogram", "second", "precision"],
        "answer": """
Measurement assigns numerical values to physical quantities using
defined units. The International System of Units (SI) includes the
metre for length, kilogram for mass, second for time, ampere for
electric current, kelvin for thermodynamic temperature, mole for
amount of substance, and candela for luminous intensity.

Precision describes the consistency of measurements, while accuracy
describes closeness to an accepted reference value. Every measurement
has uncertainty, which should be reported when relevant.

Correct units, significant figures, calibration, and clear records
are essential for reproducible experiments and reliable calculations.
"""
    },
    {
        "title": "Materials Science",
        "category": "Technology",
        "keywords": ["materials science", "metal", "polymer", "ceramic",
                     "alloy", "material properties"],
        "answer": """
Materials science examines how a material's structure relates to its
properties and performance. Major classes include metals, ceramics,
polymers, semiconductors, and composites. Properties such as strength,
hardness, flexibility, conductivity, and corrosion resistance depend
on composition and internal structure.

Engineers select materials based on the demands of a particular use,
including temperature, load, cost, safety, and environmental impact.
Materials research supports bridges, aircraft, batteries, medical
implants, electronics, and renewable-energy systems.

Testing and quality control help ensure that a material performs
as expected under real operating conditions.
"""
    },
    {
        "title": "Scientific Ethics",
        "category": "General Science",
        "keywords": ["ethics", "research ethics", "plagiarism",
                     "data integrity", "responsible science"],
        "answer": """
Scientific ethics concerns responsible conduct in research. Researchers
should report methods and results honestly, avoid fabrication and
plagiarism, acknowledge contributions, protect participants when
relevant, and disclose conflicts of interest.

Data should not be selectively altered to create a preferred result.
Uncertainty and limitations should be reported clearly. Respectful
collaboration, proper citations, reproducible methods, and independent
scrutiny help build public trust.

Ethical research is not only about following rules; it also means
being willing to correct mistakes and distinguish evidence from
personal belief.
"""
    },
    {
        "title": "SciChatAI Project",
        "category": "About SciChatAI",
        "keywords": ["scichatai", "about scichatai", "leadership",
                     "legal advisor", "chairperson", "founder"],
        "answer": """
SciChatAI is an educational science-chatbot demonstration created
to make introductory science explanations easier to explore.

Leadership listed for this project:
Legal Advisor: PARKSHITH K NAIK
Chairperson: PRATIBHA VENKATESH
Founder: JEEVAN RATHOD V

SciChatAI provides built-in educational answers using topic matching.
It does not currently connect to a live AI model or verify every
scientific claim online. Use trusted textbooks and scientific sources
for important academic work.

Copyright (c) 2026 SciChatAI.
"""
    },
]


# Twenty question forms per topic create at least 500 built-in
# question variations. The chatbot matches a question to a topic and
# returns that topic's detailed educational explanation.
QUESTION_TEMPLATES = [
    "What is {topic}?",
    "Explain {topic}.",
    "Can you explain {topic} in detail?",
    "Give me a detailed answer about {topic}.",
    "How does {topic} work?",
    "Why is {topic} important?",
    "Describe the basics of {topic}.",
    "Teach me about {topic}.",
    "What should students know about {topic}?",
    "Give me an introduction to {topic}.",
    "What are the main principles of {topic}?",
    "Explain the applications of {topic}.",
    "What are the important facts about {topic}?",
    "Help me understand {topic}.",
    "Give me a science note on {topic}.",
    "Explain the concepts behind {topic}.",
    "What is the significance of {topic}?",
    "Summarise {topic} for a student.",
    "Tell me more about {topic}.",
    "Give me a long educational explanation of {topic}.",
]

BUILT_IN_QUESTION_COUNT = len(TOPICS) * len(QUESTION_TEMPLATES)


def clean_text(text):
    """Normalise text to make question matching more reliable."""
    return re.sub(r"[^a-z0-9\s]", " ", text.lower()).strip()


def make_about_answer():
    return (
        "ABOUT SCICHATAI\n\n"
        "SciChatAI is an educational science chatbot designed to help "
        "students explore science topics through clear explanations.\n\n"
        "PROJECT LEADERSHIP\n"
        "Legal Advisor: PARKSHITH K NAIK\n"
        "Founder: JEEVAN RATHOD V\n"
        "Chairperson: PRATIBHA VENKATESH\n\n"
        "ABOUT THE FOUNDER\n"
        + FOUNDER_PROFILE
        + "\n"
        "The founder biography and research descriptions above are "
        "profile information supplied for this project and have not "
        "been independently verified by this chatbot. The named "
        "research concepts are hypotheses, not established scientific "
        "facts unless supported by published evidence.\n\n"
        "BUILT-IN QUESTION BANK\n"
        f"SciChatAI generates {BUILT_IN_QUESTION_COUNT} question "
        "variations from its built-in topic bank and question templates. "
        "This is a count of question patterns, not a claim that every "
        "variation has a separately researched answer.\n\n"
        "TECHNICAL NOTE\n"
        "This version runs on your own computer using Python's standard "
        "library. It does not require an API key. Answers come from "
        "the built-in educational topic bank, not live internet search.\n\n"
        "Copyright (c) 2026 SciChatAI."
    )


def leadership_answer(question):
    """Answer direct questions about project leadership."""
    q = clean_text(question)

    legal_words = ["legal advisor", "legal adviser", "law advisor"]
    chair_words = ["chairperson", "chair person", "chairman"]
    founder_words = ["founder", "who created", "who made", "creator"]

    if any(word in q for word in legal_words):
        return "The Legal Advisor of SciChatAI is PARKSHITH K NAIK."

    if any(word in q for word in chair_words):
        return "The Chairperson of SciChatAI is PRATIBHA VENKATESH."

    if any(word in q for word in founder_words):
        return "The Founder of SciChatAI is JEEVAN RATHOD V."

    if ("who" in q and "scichatai" in q and
            any(word in q for word in ["team", "leader", "leadership"])):
        return (
            "SciChatAI project leadership:\n"
            "Legal Advisor: PARKSHITH K NAIK\n"
            "Founder: JEEVAN RATHOD V\n"
            "Chairperson: PRATIBHA VENKATESH"
        )

    return None


def get_topic_answer(question):
    """Find the best matching built-in science topic."""
    q = clean_text(question)

    if not q:
        return (
            "Please type a science question. For example: "
            "'Explain physics', 'What is DNA?', or "
            "'Why is climate change important?'"
        )

    greeting = q.strip()
    if greeting in {"hi", "hello", "hey", "hii", "hiii", "hiya", "namaste", "good morning", "good afternoon", "good evening"}:
        return (
            "Hello and welcome to SciChatAI! 👋\n\n"
            "I'm glad you're here. I'm your learning companion for science, "
            "mathematics, technology, computers, and engineering.\n\n"
            "Ask me anything from the built-in knowledge bank, or choose a "
            "subject from the panel. What would you like to explore today?"
        )
    if greeting in {"thanks", "thank you", "thank u", "thx"}:
        return "You're very welcome! 😊 Stay curious and keep asking great questions."
    if greeting in {"bye", "goodbye", "see you", "see you later"}:
        return "Goodbye! 👋 Keep exploring, learning, and asking questions."

    if any(phrase in q for phrase in [
        "about scichatai", "what is scichatai", "about this project",
        "about the project", "tell me about scichatai"
    ]):
        return make_about_answer()

    if any(phrase in q for phrase in [
        "about jeevan", "who is jeevan", "jeevan rathod",
        "founder profile", "profile of the founder"
    ]):
        return "ABOUT JEEVAN RATHOD V\n\n" + FOUNDER_PROFILE + (
            "\nNote: This profile was supplied for the project and has "
            "not been independently verified by SciChatAI. Proposed "
            "research concepts should not be treated as established "
            "scientific discoveries without supporting evidence."
        )

    leadership = leadership_answer(question)
    if leadership:
        return leadership

    # Prefer exact title matches and keyword matches.
    best_topic = None
    best_score = 0
    words = set(q.split())

    stop_words = {
        "what", "is", "are", "the", "a", "an", "of", "to", "in", "on",
        "for", "and", "or", "how", "why", "explain", "tell", "me",
        "about", "give", "can", "you", "please", "with", "does",
        "do", "work", "more", "detail", "detailed", "long", "answer",
        "important", "basics", "student", "students", "science", "note",
    }
    useful_words = words - stop_words

    for topic in TOPICS:
        title = clean_text(topic["title"])
        score = 0

        if title and title in q:
            score += 10

        for keyword in topic["keywords"]:
            normal_keyword = clean_text(keyword)

            if normal_keyword and normal_keyword in q:
                score += 5

            keyword_words = set(normal_keyword.split())
            score += len(useful_words.intersection(keyword_words))

        if score > best_score:
            best_score = score
            best_topic = topic

    if best_topic and best_score >= 2:
        return (
            best_topic["title"].upper()
            + "\n\n"
            + best_topic["answer"].strip()
            + "\n\n"
            + "Explore further: ask a follow-up question, compare this "
              "topic with another subject, or consult a trusted "
              "textbook or scientific reference."
        )

    return (
        "I'm still expanding my built-in knowledge bank, so I couldn't "
        "find a reliable answer to that question yet. 📚\n\n"
        "I'm learning topic by topic. Try rephrasing your question or "
        "choosing a subject from the panel. You can also use the Search "
        "Web button to look up your question in your browser.\n\n"
        "This demo works without a paid API and does not automatically "
        "verify live web results. Please cross-check important facts with "
        "trusted educational sources."
    )


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#080e1d">
<title>SciChatAI — Explore Science</title>
<style>
:root {
  --bg:#080e1d; --panel:#101a2d; --panel2:#14213a;
  --line:#263753; --text:#eef5ff; --muted:#a5b5cc;
  --blue:#6ba7ff; --cyan:#66e4df; --purple:#b69cff;
}
* { box-sizing:border-box; }
body {
  margin:0; min-height:100vh; color:var(--text);
  background:radial-gradient(ellipse at 10% 0%,#172b4d 0,transparent 42%),
             radial-gradient(ellipse at 100% 20%,#1a2044 0,transparent 35%),
             var(--bg);
  font-family:Inter,Segoe UI,Arial,sans-serif;
}
button,textarea { font:inherit; }
button { cursor:pointer; }
header {
  padding:22px clamp(16px,4vw,52px); display:flex;
  align-items:center; justify-content:space-between; gap:15px;
  border-bottom:1px solid #263753aa; backdrop-filter:blur(12px);
}
.brand { display:flex; gap:12px; align-items:center; }
.logo {
  width:48px;height:48px;display:grid;place-items:center;
  border-radius:16px;font-size:25px;
  background:linear-gradient(135deg,#3c83f6,#7a63ee);
  box-shadow:0 8px 28px #417df544;
}
.brand h1 { margin:0;font-size:clamp(20px,3vw,29px);letter-spacing:-1px; }
.brand p { margin:4px 0 0;color:var(--muted);font-size:12px; }
.status {
  border:1px solid #285c5a;background:#103331;color:#9bf3df;
  padding:8px 12px;border-radius:99px;font-size:12px;white-space:nowrap;
}
main { width:min(1180px,94%); margin:32px auto; }
.hero { text-align:center;padding:24px 10px 28px; }
.eyebrow { color:var(--cyan);font-size:12px;letter-spacing:3px;font-weight:800; }
.hero h2 { font-size:clamp(32px,5vw,54px);line-height:1.08;margin:15px 0;letter-spacing:-2px; }
.gradient {
  background:linear-gradient(90deg,#80b6ff,#7ee9df,#c4a5ff);
  color:transparent;background-clip:text;-webkit-background-clip:text;
}
.hero p { max-width:680px;margin:0 auto;color:var(--muted);line-height:1.7; }
.stats { display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-top:22px; }
.stat { padding:10px 14px;background:var(--panel);border:1px solid var(--line);border-radius:12px;font-size:13px;color:var(--muted); }
.stat strong { color:var(--text); }
body:not(.dark) .subject:hover, body:not(.dark) .subject.active { color:#17243b;background:#e5eefb;border-color:#c2d5ef; }
body:not(.dark) .quick button { border-color:var(--line);background:var(--panel2);color:var(--text); }
body:not(.dark) textarea { color:var(--text);background:#fff;border-color:#cbd7e7; }
body:not(.dark) .tip { background:#edf4fd;color:var(--muted); }
body:not(.dark) .person { background:var(--panel2); }
.layout { display:grid;grid-template-columns:270px minmax(0,1fr);gap:18px;align-items:start; }
.panel { background:#101a2deF;border:1px solid var(--line);border-radius:20px;overflow:hidden; }
.panel-head { padding:18px 18px 12px;font-weight:800; }
.sidebar { padding:0 12px 14px; }
.subject {
  width:100%;text-align:left;color:var(--muted);background:transparent;
  border:1px solid transparent;border-radius:11px;padding:11px 12px;
  margin:2px 0;transition:.2s;
}
.subject:hover,.subject.active { color:white;background:#203453;border-color:#3c5d8b; }
.tip { padding:15px 17px;margin:0 12px 15px;border-radius:13px;
  background:#172844;color:var(--muted);font-size:12px;line-height:1.6; }
.chat { display:flex;flex-direction:column;min-height:590px; }
.chat-top { display:flex;align-items:center;justify-content:space-between;gap:10px;
  padding:16px 18px;border-bottom:1px solid var(--line); }
.chat-top h3 { margin:0;font-size:16px; }
.actions { display:flex;gap:8px;flex-wrap:wrap; }
.btn { border:1px solid var(--line);color:var(--text);background:var(--panel2);
  padding:9px 12px;border-radius:10px;font-size:12px; }
.btn:hover { background:#294264; }
.btn.primary { border:0;color:#071423;font-weight:800;background:linear-gradient(100deg,#7bb8ff,#74e8db); }
.messages { padding:20px;flex:1;min-height:320px;max-height:560px;overflow:auto; }
.message { display:flex;gap:10px;margin:0 0 20px;align-items:flex-start; }
.avatar { flex:0 0 34px;width:34px;height:34px;border-radius:11px;
  display:grid;place-items:center;background:#213a5b; }
.message.user .avatar { background:#493c79; }
.bubble { min-width:0;max-width:100%;background:#15233a;border:1px solid #293d5b;
  border-radius:4px 15px 15px 15px;padding:13px 15px;line-height:1.75;
  white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px; }
.message.user { flex-direction:row-reverse; }
.message.user .bubble { background:#28244b;border-color:#49417a;border-radius:15px 4px 15px 15px; }
.message.user .content { display:flex;flex-direction:column;align-items:flex-end; }
.content { min-width:0;max-width:88%; }
.name { color:var(--cyan);font-size:11px;font-weight:800;margin:0 0 6px 2px; }
.message.user .name { color:#c8b9ff; }
.time { color:#7184a0;font-size:10px;margin:5px 4px 0; }
.composer { border-top:1px solid var(--line);padding:16px; }
.quick { display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px; }
.quick button { border:1px solid #334968;background:#14233a;color:#cbd9ee;
  border-radius:99px;padding:7px 10px;font-size:11px; }
.input-row { display:flex;gap:10px;align-items:stretch; }
textarea { flex:1;min-width:0;resize:vertical;min-height:54px;max-height:180px;
  color:var(--text);background:#091323;border:1px solid #344b6c;
  border-radius:13px;padding:15px;outline:none; }
textarea:focus { border-color:var(--blue);box-shadow:0 0 0 3px #6ba7ff22; }
.send { padding:0 20px;border-radius:13px; }
.hint { color:#8093ae;font-size:11px;margin:10px 2px 0; }
.about { margin-top:20px;padding:24px; }
.about h3 { margin-top:0; }
.about p,.about li { color:var(--muted);line-height:1.75;font-size:14px; }
.people { display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px; }
.person { padding:16px;border:1px solid var(--line);background:#111e33;border-radius:14px; }
.person span { color:var(--cyan);font-size:11px;text-transform:uppercase;letter-spacing:1px; }
.person strong { display:block;margin-top:8px;line-height:1.5; }
.links { display:flex;gap:12px;flex-wrap:wrap; }
a { color:#91c3ff;overflow-wrap:anywhere; }
footer { text-align:center;color:#8395af;font-size:12px;padding:26px 10px 35px; }
@media(max-width:800px) {
  .layout { grid-template-columns:1fr; }
  .sidebar { display:grid;grid-template-columns:repeat(2,minmax(0,1fr)); }
  .panel-head { padding-bottom:10px; }
  .tip { margin-top:8px; }
  .chat { min-height:540px; }
}
@media(max-width:520px) {
  header { align-items:flex-start; }
  .status { font-size:10px;padding:7px; }
  .people { grid-template-columns:1fr; }
  .input-row { flex-direction:column; }
  .send { min-height:46px; }
  .messages { padding:13px; }
  .content { max-width:91%; }
}

/* SciChatAI upgrade: light mode is the default */
body { --bg:#f4f7fc; --panel:#ffffff; --panel2:#edf3fb; --line:#dbe4f0; --text:#17243b; --muted:#52627a; background:radial-gradient(ellipse at 10% 0%,#e2f3ff 0,transparent 42%),radial-gradient(ellipse at 100% 20%,#eeeaff 0,transparent 35%),var(--bg); }
header { border-bottom-color:#dce5f0; }
.status { border-color:#b7e8dc; background:#e5faf3; color:#08765d; }
.panel { box-shadow:0 12px 35px #29466b0c; }
.bubble { background:#eef3fb; color:#17243b; }
.message.user .bubble { background:#dceaff; color:#173c7a; }
body.dark { --bg:#080e1d; --panel:#101a2d; --panel2:#14213a; --line:#263753; --text:#eef5ff; --muted:#a5b5cc; background:radial-gradient(ellipse at 10% 0%,#172b4d 0,transparent 42%),radial-gradient(ellipse at 100% 20%,#1a2044 0,transparent 35%),var(--bg); }
body.dark .bubble { background:#17243b; color:#eef5ff; } body.dark .message.user .bubble { background:#203d6a; color:#fff; }
.feature-tools { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; margin:22px 0; }
.feature-card { border:1px solid var(--line); background:var(--panel); color:var(--text); border-radius:16px; padding:16px; }
.feature-card h3 { margin:0 0 10px; } .feature-card p { color:var(--muted); font-size:13px; line-height:1.5; }
.feature-card button, .tool-btn { border:1px solid var(--line); border-radius:10px; padding:9px 12px; background:var(--panel2); color:var(--text); margin:4px 4px 4px 0; }
.feature-card select { max-width:100%; padding:8px; border-radius:8px; }
#quizResult { white-space:pre-wrap; line-height:1.5; margin-top:8px; }
@media(max-width:700px){ .feature-tools{grid-template-columns:1fr;} }

</style>
</head>
<body>
<header>
  <div class="brand">
    <div class="logo">⚛</div>
    <div><h1>SciChat<span class="gradient">AI</span></h1>
    <p>SCIENCE • CURIOSITY • DISCOVERY</p></div>
  </div>
  <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><button class="btn" id="themeBtn" type="button">☀️ Light mode</button><div class="status">● LOCAL DEMO ONLINE</div></div>
</header>

<main>
  <section class="hero">
    <div class="eyebrow">YOUR SCIENCE EXPLORATION LAB</div>
    <h2>Big questions.<br><span class="gradient">Clearer answers.</span></h2>
    <p>Explore science, technology, physics, biology, astronomy and more.
       Ask a question and start discovering how the world works.</p>
    <div class="stats">
      <div class="stat"><strong id="questionCount">500+</strong> question variations</div>
      <div class="stat"><strong>20</strong> question styles</div>
      <div class="stat"><strong>24/7</strong> on your computer</div>
    </div>
  </section>

  <div class="layout">
    <aside class="panel">
      <div class="panel-head">Explore subjects</div>
      <div class="sidebar" id="subjects"></div>
      <div class="tip">💡 <strong>Study tip</strong><br>
      Ask a question in your own words. For best results, mention the
      science topic clearly.</div>
    </aside>

    <section class="panel chat">
      <div class="chat-top">
        <h3>✦ SciChatAI Assistant</h3>
        <div class="actions">
          <button class="btn" id="saveBtn">↓ Save chat</button>
          <button class="btn" id="clearBtn">Clear</button>
        </div>
      </div>
      <div class="messages" id="messages" aria-live="polite"></div>
      <div class="composer">
        <div class="quick">
          <button data-q="Explain general science">General science</button>
          <button data-q="Explain quantum physics">Quantum physics</button>
          <button data-q="What is the universe?">The universe</button>
          <button data-q="About SciChatAI">About SciChatAI</button>
        </div>
        <div class="input-row">
          <textarea id="question" placeholder="Ask SciChatAI a question..."
            aria-label="Your science question"></textarea>
          <button class="btn" id="micBtn" type="button" title="Speak your question">🎙️ Speak</button>
          <button class="btn" id="searchWebBtn" type="button" title="Search this question in your browser">🌐 Search web</button>
          <button class="btn primary send" id="sendBtn">Ask ↗</button>
        </div>
        <div class="hint">Press Enter to ask • Shift + Enter for a new line</div>
      </div>
    </section>
  </div>


  <section class="feature-tools" aria-label="Learning tools">
    <div class="feature-card"><h3>📚 Course explorer</h3><p>Choose a subject to explore the built-in knowledge bank.</p><select id="courseSelect" aria-label="Choose a course"><option>Loading topics…</option></select><button id="courseGo" type="button">Explore topic</button></div>
    <div class="feature-card"><h3>🧠 Science quiz</h3><p>Try a multiple-choice question, check your answer, and learn why.</p><div id="quizQuestion"></div><div id="quizOptions"></div><div id="quizResult" aria-live="polite"></div><button id="nextQuiz" type="button">Next question</button><p id="quizScore">Score: 0</p></div>
    <div class="feature-card"><h3>🎙️ Voice & web search</h3><p>Use speech recognition if your browser supports it. Search the web when the offline bank does not cover a topic.</p><button id="micBtn" type="button">🎙️ Start microphone</button><button id="webBtn" type="button">🔎 Search web</button><p id="micStatus" aria-live="polite">Microphone is ready when supported and permission is granted.</p></div>
    <div class="feature-card"><h3>💡 Try asking</h3><p>Click a suggested question to send it to SciChatAI.</p><div id="suggestedQuestions"></div></div>
  </section>

  <section class="panel about" id="about">
    <h3>About SciChatAI</h3>
    <p>SciChatAI is a student-oriented educational chatbot demonstration
       built with Python. It provides prepared explanations across science
       subjects and helps users explore ideas through a simple web interface.</p>
    <div class="people">
      <div class="person"><span>Legal Advisor</span><strong>PARKSHITH K NAIK</strong></div>
      <div class="person"><span>Chairperson</span><strong>PRATIBHA VENKATESH</strong></div>
      <div class="person"><span>Founder</span><strong>JEEVAN RATHOD V</strong></div>
    </div>
    <h3 style="margin-top:24px">Founder profile — Jeevan Rathod V</h3>
    <p>According to the profile supplied for this project, Jeevan Rathod V
       is an independent young researcher from Davanagere, Karnataka, India,
       with interests in theoretical physics and cosmology. His stated
       research interests include the proposed Infinite Rathod's Particles
       (R-P) framework, the White Paper Cosmos Hypothesis, the cosmological
       constant, and the vacuum catastrophe.</p>
    <p>These descriptions are presented as supplied profile information,
       not independently verified claims. The named concepts are hypotheses
       or proposed ideas and should not be treated as established scientific
       discoveries without reliable evidence and independent review.</p>
    <div class="links">
      <a href="https://sites.google.com/view/davangeresyoungestresearcherin" target="_blank" rel="noopener">Portfolio ↗</a>
      <a href="https://in.linkedin.com/in/jeevan-rathod-v-b471493ba" target="_blank" rel="noopener">LinkedIn ↗</a>
      <a href="https://www.youtube.com/@jeevanrathodv" target="_blank" rel="noopener">YouTube ↗</a>
      <a href="https://orcid.org/0009-0001-4317-003X" target="_blank" rel="noopener">ORCID ↗</a>
    </div>
    <h3 style="margin-top:24px">How it works</h3>
    <p>This demonstration runs locally on the computer hosting Python.
       Its built-in question variations are generated from topic names
       and question templates. It does not currently connect to a live
       AI model or search the internet, and its answers should be checked
       against trusted educational sources when accuracy is important.</p>
  </section>
</main>

<footer>Made for curious minds · Copyright © 2026 SciChatAI</footer>

<script>
const SUBJECTS = [
  ["✦","All subjects"],
  ["🔬","General Science"],
  ["⚙️","Physics"],
  ["🧪","Chemistry"],
  ["🧬","Biology"],
  ["📐","Mathematics"],
  ["🌌","Astronomy"],
  ["🌍","Earth Science"],
  ["🌱","Environment"],
  ["💻","Computer Science"],
  ["🤖","Technology"],
  ["ℹ️","About SciChatAI"]
];

const subjectBox = document.getElementById("subjects");
const messages = document.getElementById("messages");
const input = document.getElementById("question");
const sendBtn = document.getElementById("sendBtn");
const saveBtn = document.getElementById("saveBtn");
const clearBtn = document.getElementById("clearBtn");
const micBtn = document.getElementById("micBtn");
const searchWebBtn = document.getElementById("searchWebBtn");
let historyItems = [];

function startVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this browser. Try the latest Chrome or Edge, or type your question instead.");
    return;
  }
  const recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  micBtn.disabled = true;
  micBtn.textContent = "🎙️ Listening…";
  recognition.onresult = event => {
    input.value = event.results[0][0].transcript;
    input.focus();
  };
  recognition.onerror = event => {
    alert(event.error === "not-allowed"
      ? "Microphone permission was denied. Allow microphone access in your browser settings."
      : "Microphone input was unavailable. Please type your question instead.");
  };
  recognition.onend = () => {
    micBtn.disabled = false;
    micBtn.textContent = "🎙️ Speak";
  };
  try { recognition.start(); }
  catch (error) {
    micBtn.disabled = false;
    micBtn.textContent = "🎙️ Speak";
    alert("Could not start the microphone. Please try again or type your question.");
  }
}

micBtn.addEventListener("click", startVoiceInput);
searchWebBtn.addEventListener("click", () => {
  const query = input.value.trim();
  if (!query) {
    input.focus();
    alert("Type a question first, then press Search web.");
    return;
  }
  window.open("https://www.google.com/search?q=" + encodeURIComponent(query), "_blank", "noopener,noreferrer");
});
let activeSubject = "All subjects";

function addSubjectButtons() {
  SUBJECTS.forEach(([icon, name], index) => {
    const button = document.createElement("button");
    button.className = "subject" + (index === 0 ? " active" : "");
    button.textContent = icon + "  " + name;
    button.addEventListener("click", () => {
      activeSubject = name;
      document.querySelectorAll(".subject").forEach(el => el.classList.remove("active"));
      button.classList.add("active");
      if (name === "About SciChatAI") {
        document.getElementById("about").scrollIntoView({behavior:"smooth"});
      } else if (name !== "All subjects") {
        input.value = "Explain " + name;
        input.focus();
      }
    });
    subjectBox.appendChild(button);
  });
}

function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = "message " + role;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "👤" : "⚛";
  const content = document.createElement("div");
  content.className = "content";
  const name = document.createElement("div");
  name.className = "name";
  name.textContent = role === "user" ? "YOU" : "SCICHATAI";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  const time = document.createElement("div");
  time.className = "time";
  time.textContent = new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"});
  content.append(name, bubble, time);
  row.append(avatar, content);
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
}

function showWelcome() {
  messages.innerHTML = "";
  addMessage("bot",
    "Welcome to SciChatAI! 👋\n\n" +
    "I'm ready to help you explore science. Ask about physics, chemistry, " +
    "biology, astronomy, mathematics, computers, or the environment.\n\n" +
    "Try: “Explain quantum physics” or “What is DNA?”\n\n" +
    "This demo uses a built-in educational knowledge bank. For important " +
    "schoolwork, always cross-check information with trusted sources.");
}

async function askQuestion(text) {
  const question = text.trim();
  if (!question) {
    input.focus();
    return;
  }

  historyItems.push({role:"You", text:question, time:new Date().toLocaleString()});
  addMessage("user", question);
  input.value = "";
  sendBtn.disabled = true;
  sendBtn.textContent = "Thinking…";

  try {
    const response = await fetch("/ask", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({question:question})
    });
    if (!response.ok) throw new Error("Server returned " + response.status);
    const data = await response.json();
    const answer = data.answer || "Sorry, no answer was returned.";
    addMessage("bot", answer);
    historyItems.push({role:"SciChatAI", text:answer, time:new Date().toLocaleString()});
  } catch (error) {
    const message = "I couldn't reach the local Python server. Check that " +
      "the SciChatAI Python window is still running, then refresh this page.";
    addMessage("bot", message);
    historyItems.push({role:"SciChatAI", text:message, time:new Date().toLocaleString()});
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Ask ↗";
    input.focus();
  }
}

sendBtn.addEventListener("click", () => askQuestion(input.value));
input.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    askQuestion(input.value);
  }
});

document.querySelectorAll("[data-q]").forEach(button => {
  button.addEventListener("click", () => askQuestion(button.dataset.q));
});

clearBtn.addEventListener("click", () => {
  historyItems = [];
  showWelcome();
});

saveBtn.addEventListener("click", () => {
  if (!historyItems.length) {
    alert("Ask at least one question before saving your chat.");
    return;
  }
  const content = [
    "SciChatAI — Saved Conversation",
    "Copyright © 2026 SciChatAI",
    "Saved: " + new Date().toLocaleString(),
    "=".repeat(45),
    "",
    ...historyItems.map(item =>
      "[" + item.time + "] " + item.role + ":\\n" + item.text + "\\n"
    )
  ].join("\\n");
  const blob = new Blob([content], {type:"text/plain;charset=utf-8"});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "SciChatAI_Chat.txt";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
});

async function loadInfo() {
  try {
    const response = await fetch("/health");
    const data = await response.json();
    document.getElementById("questionCount").textContent =
      data.question_variations + "+";
  } catch (error) {
    // The interface can still render if the status request fails.
  }
}


// Added learning tools. Uses existing /ask endpoint and original TOPICS data.
const QUIZ = [
 {q:"Which gas do plants absorb during photosynthesis?", options:["Oxygen","Carbon dioxide","Nitrogen","Hydrogen"], correct:1, why:"Plants use carbon dioxide and water to make sugars using light energy."},
 {q:"What is the SI unit of force?", options:["Joule","Watt","Newton","Pascal"], correct:2, why:"Force is measured in newtons (N)."},
 {q:"Which part of an atom has a positive charge?", options:["Electron","Proton","Neutron","Photon"], correct:1, why:"Protons have positive charge; electrons are negative and neutrons are neutral."},
 {q:"What does DNA primarily store?", options:["Genetic information","Sound waves","Heat energy only","Magnetic fields"], correct:0, why:"DNA contains genetic instructions used in growth, development, and cell function."},
 {q:"What is the value of 2² + 3²?", options:["10","12","13","25"], correct:2, why:"2² + 3² = 4 + 9 = 13."},
 {q:"Which planet is known as the Red Planet?", options:["Venus","Mars","Jupiter","Mercury"], correct:1, why:"Iron-rich dust gives Mars its reddish appearance."},
 {q:"What does HTML help define?", options:["Webpage structure","Battery chemistry","Gravity","CPU temperature"], correct:0, why:"HTML describes the structure and content of webpages."},
 {q:"Which is a renewable energy source?", options:["Coal","Petrol","Solar energy","Natural gas"], correct:2, why:"Solar energy is replenished by sunlight."}
];
let quizIndex=0, quizScore=0, quizAnswered=false;
function renderQuiz(){const q=QUIZ[quizIndex]; quizAnswered=false; document.getElementById('quizQuestion').textContent=(quizIndex+1)+'. '+q.q; const box=document.getElementById('quizOptions'); box.replaceChildren(); q.options.forEach((label,i)=>{const b=document.createElement('button');b.type='button';b.textContent=String.fromCharCode(65+i)+'. '+label;b.onclick=()=>{if(quizAnswered)return;quizAnswered=true;const ok=i===q.correct;if(ok)quizScore++;document.getElementById('quizResult').textContent=(ok?'✅ Correct! ':'❌ Not quite. ')+q.why;document.getElementById('quizScore').textContent='Score: '+quizScore;box.querySelectorAll('button').forEach(x=>x.disabled=true);};box.appendChild(b);});document.getElementById('quizResult').textContent='';}
document.getElementById('nextQuiz').addEventListener('click',()=>{quizIndex=(quizIndex+1)%QUIZ.length;if(quizIndex===0)quizScore=0;renderQuiz();document.getElementById('quizScore').textContent='Score: '+quizScore;});
const courseSelect=document.getElementById('courseSelect');
const topicTitles=["General Science", "Physics", "Chemistry", "Biology", "Mathematics", "Astronomy", "Earth Science", "Environmental Science", "Computer Science", "Artificial Intelligence", "Human Body", "Genetics and DNA", "Evolution", "Electricity", "Magnetism", "Light and Optics", "Sound and Waves", "Thermodynamics", "Quantum Physics", "Relativity", "The Solar System", "The Universe", "Black Holes", "Climate and Weather", "Oceans", "Plants and Photosynthesis", "Microbiology", "Human Health and Nutrition", "Probability and Statistics", "Robotics", "Renewable Energy", "Scientific Research", "Scientific Units and Measurement", "Materials Science", "Scientific Ethics", "SciChatAI Project"];
courseSelect.replaceChildren();topicTitles.forEach(t=>{const o=document.createElement('option');o.value=t;o.textContent=t;courseSelect.appendChild(o);});
document.getElementById('courseGo').addEventListener('click',()=>{input.value='Explain '+courseSelect.value;askQuestion(input.value);});
const suggestions=['What is photosynthesis?','Explain Newton’s laws of motion','What is DNA?','How does electricity work?','Explain machine learning','What causes seasons?','What is the water cycle?','Teach me Python basics'];
const sugBox=document.getElementById('suggestedQuestions');suggestions.forEach(q=>{const b=document.createElement('button');b.type='button';b.textContent=q;b.onclick=()=>askQuestion(q);sugBox.appendChild(b);});
// Keep conversation during this browser session, including page refreshes.
const originalAddMessage=addMessage;
function restoreSession(){try{const saved=JSON.parse(sessionStorage.getItem('scichatai_history')||'[]');if(saved.length){historyItems=saved;messages.replaceChildren();saved.forEach(m=>originalAddMessage(m.role==='You'?'user':'bot',m.text));}}catch(e){}}
const originalAskQuestion=askQuestion;
askQuestion=async function(text){await originalAskQuestion(text);try{sessionStorage.setItem('scichatai_history',JSON.stringify(historyItems));}catch(e){}};
clearBtn.addEventListener('click',()=>{try{sessionStorage.removeItem('scichatai_history');}catch(e){};});
const themeBtn=document.getElementById('themeBtn');
function setTheme(dark){document.body.classList.toggle('dark',dark);themeBtn.textContent=dark?'🌙 Dark mode':'☀️ Light mode';try{localStorage.setItem('scichatai_theme',dark?'dark':'light');}catch(e){}}
let initialDark=false;try{initialDark=localStorage.getItem('scichatai_theme')==='dark';}catch(e){}setTheme(initialDark);themeBtn.addEventListener('click',()=>setTheme(!document.body.classList.contains('dark')));
function searchCurrentQuestion(){const q=input.value.trim();if(!q){document.getElementById('micStatus').textContent='Type a question first, then press Search web.';input.focus();return;}window.open('https://www.google.com/search?q='+encodeURIComponent(q+' science education'),'_blank','noopener,noreferrer');}
document.getElementById('webBtn').addEventListener('click',searchCurrentQuestion);
document.getElementById('micBtn').addEventListener('click',()=>{const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;const status=document.getElementById('micStatus');if(!Recognition){status.textContent='Speech recognition is not supported in this browser. Try Chrome or Edge, or type your question.';return;}const rec=new Recognition();rec.lang='en-IN';rec.interimResults=false;rec.maxAlternatives=1;rec.onstart=()=>status.textContent='Listening… Speak clearly.';rec.onresult=e=>{input.value=e.results[0][0].transcript;status.textContent='Captured: “'+input.value+'” — press Ask to submit.';input.focus();};rec.onerror=e=>{const msgs={'not-allowed':'Microphone permission was denied. Allow microphone access in your browser settings.','no-speech':'No speech detected. Try again in a quieter place.',network:'Speech recognition network unavailable. You can still type.','audio-capture':'No microphone was detected.'};status.textContent=msgs[e.error]||('Microphone error: '+e.error+'. You can type instead.');};rec.onend=()=>{if(status.textContent==='Listening… Speak clearly.')status.textContent='Listening stopped. Tap the microphone to try again.';};try{rec.start();}catch(e){status.textContent='Could not start microphone. Check browser permission and try again.';}});
renderQuiz();

addSubjectButtons();
showWelcome();
restoreSession();
loadInfo();
</script>
</body>
</html>
"""


class SciChatAIHandler(BaseHTTPRequestHandler):
    """Serve the SciChatAI web interface and chatbot answers."""

    def send_text(self, status, text, content_type="text/plain; charset=utf-8"):
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False)
        self.send_text(status, body, "application/json; charset=utf-8")

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            self.send_text(200, HTML_PAGE, "text/html; charset=utf-8")
            return

        if path == "/health":
            self.send_json(200, {
                "status": "online",
                "app": APP_NAME,
                "question_variations": BUILT_IN_QUESTION_COUNT,
                "topics": len(TOPICS),
                "time": datetime.now().isoformat(timespec="seconds"),
            })
            return

        self.send_text(404, "Page not found.")

    def do_POST(self):
        path = urlparse(self.path).path

        if path != "/ask":
            self.send_json(404, {"error": "Endpoint not found."})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))

            if length <= 0 or length > 20000:
                self.send_json(400, {"error": "Please send a shorter question."})
                return

            raw_body = self.rfile.read(length)
            payload = json.loads(raw_body.decode("utf-8"))
            question = str(payload.get("question", "")).strip()

            if not question:
                self.send_json(400, {
                    "error": "Please type a question first."
                })
                return

            if len(question) > 2000:
                self.send_json(400, {
                    "error": "Please keep your question under 2000 characters."
                })
                return

            answer = get_topic_answer(question)
            self.send_json(200, {"answer": answer})

        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "The request was not valid JSON."})
        except Exception:
            self.send_json(500, {
                "error": "Something went wrong while preparing the answer."
            })

    def log_message(self, format_string, *args):
        # Keep the terminal tidy while still showing useful server activity.
        print("[SciChatAI]", format_string % args)


def main():
    print("=" * 56)
    print(" SciChatAI — Educational Science Chatbot")
    print(" Copyright (c) 2026 SciChatAI")
    print("=" * 56)
    print("Built-in topics:", len(TOPICS))
    print("Question variations:", BUILT_IN_QUESTION_COUNT)
    print("Local website: http://127.0.0.1:" + str(PORT))
    if HOST == "0.0.0.0":
        print("Public hosting mode enabled (bound to all interfaces).")
    print("Keep this Python window open while using SciChatAI.")
    print("Press Ctrl+C in this window to stop the server.")
    print("=" * 56)

    try:
        server = ThreadingHTTPServer((HOST, PORT), SciChatAIHandler)
    except OSError as error:
        print("\nCould not start SciChatAI on port", PORT)
        print("The port may already be in use.")
        print("Close another SciChatAI window or restart your computer.")
        print("Technical detail:", error)
        input("\nPress Enter to close...")
        return

    try:
        if HOST == "127.0.0.1":
            threading.Timer(
                1.0,
                lambda: webbrowser.open("http://127.0.0.1:" + str(PORT))
            ).start()
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSciChatAI is shutting down...")
    finally:
        server.server_close()
        print("SciChatAI server stopped.")


if __name__ == "__main__":
    main()

Calphad Databases
=================

Calphad database files contain model parameters for Gibbs energy and thermophysical properties of indvididual phases.
They are commonly stored and distributed in the following formats:

- Thermodynamic DataBase (``.tdb``) format (most common for open databases)
- ChemSage (``.dat``) format
- Commercial encrypted databases (not able to be read by PyCalphad)
- Emerging XML-based formats (`PyCalphad-XML <https://github.com/pycalphad/pycalphad-xml>`_, `XTDB <https://doi.org/10.1016/j.calphad.2025.102849>`_, `ThermML <https://github.com/flotang-gtt/ThermML>`_)

PyCalphad natively has ability parse databases saved with the file extension ``.tdb`` or ``.dat``.
It can be extended via a plugin system to understand other formats (see `PyCalphad-XML <https://github.com/pycalphad/pycalphad-xml>`_, which is deployed as a plugin that allows PyCalphad to understand the ``.xml`` extension).
These files are read by PyCalphad by importing and creating an instance of the ``Database`` class:

.. code-block:: python

   from pycalphad import Database
   db = Database("path/to/database.tdb")


.. _calphad-database-verification-boundaries:

Specialized model verification boundaries
-----------------------------------------

Support for a specialized model is not a general compatibility or accuracy
guarantee. The statements below describe the bounded regression contracts
exercised by PyCalphad's bundled test fixtures. They do not establish that an
arbitrary database will parse, that its thermodynamic assessment is correct, or
that an equilibrium or phase-boundary calculation will converge throughout a
composition-temperature domain.

Two kinds of evidence are kept distinct:

- **External point oracles** compare selected model or equilibrium values with
  values recorded from Thermochimica, FactSage, or Thermo-Calc.
- **Structural regressions** check internal consistency, such as coordinate
  normalization, charge and site-balance constraints, finite degrees of
  freedom, and continuation status. Structural regressions are not independent
  thermodynamic validation.

The fixture source, evidence status, claim boundary, canonical LF-normalized
SHA-256 digest, and resolving test are recorded in
``pycalphad/tests/test_benchmark_provenance.py``. The manifest also records when
an explicit redistribution license has not been established; inclusion in the
test suite must not be interpreted as a general redistribution grant.

Modified quasichemical model in the quadruplet approximation (MQMQA)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **DAT parsing:** selected ``SUBQ`` reciprocal records, including one ``MQMX``
  term in the Dixon Na-K-Cl-I fixture, and selected ``SUBG`` coordination-number
  ordering are covered by semantic parser tests. This does not qualify every
  ChemSage record type, temperature branch, chemical-group combination, or
  MQMQA database.
- **Direct model evaluation:** the Shishin Fe-Sb-O-S ``SUBQ`` fixture has
  external point-energy comparisons and structural checks for coordinate and
  pair normalization, element accounting, charge residuals, finite
  thermodynamic properties, and ``HM = GM + T*SM`` at explicitly selected
  states. These checks do not validate arbitrary endpoints, systems, or
  composition-temperature extrapolation.
- **Equilibrium:** the Dixon reciprocal ``MSCL`` model has one external FactSage
  equilibrium Gibbs-energy comparison at 800 K. It is not evidence for general
  phase-boundary topology, reciprocal-parameter coverage, or solver convergence.
- **Mapping:** a Na-K-Cl projection of the Dixon fixture checks that coexistence
  mapping preserves ``X(CL) = 0.5``, variable ordering, finite quadruplet
  degrees of freedom no smaller than ``-1e-12``, quadruplet normalization, and
  internal constraints. No external
  phase-boundary oracle is asserted, and this does not qualify I-containing
  reciprocal sections or MQMQA mapping in general.
- **Known API boundary:** MQMQA reference-state shifting and reference models
  are not implemented; ``ModelMQMQA.shift_reference_state`` and the reference
  model API raise ``NotImplementedError``.

Charged compound-energy formalism (CEF) and ionic liquids
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Charged CEF equilibrium:** one Ti-O stoichiometric two-phase equilibrium has
  internal convergence, phase-amount, mass-balance, and chemical-potential
  regressions. One Al-Fe-O equilibrium point is compared with Thermo-Calc, but
  its fixture source publication is not recorded. These checks do not qualify
  complex oxide CEF databases broadly or arbitrary charge-balanced sublattice
  topologies.
- **Charged CEF mapping:** one Ti-O two-phase temperature continuation checks
  both hard-axis endpoints, phase identity, finite site fractions, and internal
  constraints. It is a structural regression without an external phase-boundary
  oracle, not a general charged-oxide mapping guarantee.
- **Phase-local feasibility diagnostics:** generated constitution samples can
  distinguish feasible and infeasible phase-local mole-fraction conditions for
  selected charged and fixed-composition phases. The warning reports sampling
  failure for those conditions; it is not a proof of physical infeasibility and
  is intentionally distinct from invalid caller-provided points or a later
  equilibrium-solver failure.
- **Two-sublattice ionic liquid:** for phases marked with the two-sublattice
  ionic-liquid model, construction requires exactly two constituent sublattices
  and two site ratios. A synthetic singleton-cation and neutral-species case is
  analytically checked against a regular solution. This does not establish
  general multi-cation/neutral extrapolation or reassess any ionic-liquid
  database.


Obtaining Calphad Databases
---------------------------

It is increasingly common (and required by some journals) for authors to publish their database files in Calphad assessment papers.
In the case they are not published, they can usually be constructed by hand from tables of model parameters in the assessment papers.

Many database files have been indexed and made availale through various community efforts (in no particular order):

- The `TDBDB <https://avdwgroup.engin.brown.edu/>`_ can be used to search for TDB included with publications
- `NIMS <https://cpddb.nims.go.jp>`_ (registration required) provides a collection of binary and ternary databases
- `NIST Materials Data <https://materialsdata.nist.gov/handle/11256/8>`_ repository contains databases deposited by authors
- `NIST solder database <https://www.metallurgy.nist.gov/phase/solder/solder.html>`_
- `Innomat AB <https://www.innomat.se/thermodynamic-databases/>`_ provide several multi-component databases
- `MatCalc <https://www.matcalc.at/index.php/databases/open-databases>`_ provide several multi-component databases
- `LibreCalphad <https://github.com/mfrichtl/librecalphad>`_ maintained by Matt Frichtl contains a multi-component steel database
- `PhaseDiagrams.org <https://phasediagrams.org>`_ provides a browsable set of binary assessments, mostly populated by the `SGTE binary collection by Bengt Hallstedt <https://doi.org/10.1016/j.calphad.2025.102833>`_.


If you would like to perform your own Calphad assessments using PyCalphad, check out `ESPEI <https://espei.org/>`_!

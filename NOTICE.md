# Notice and design influences

Humanizer JA Editor is an original implementation. Its architecture was informed by publicly available writing-editing skills and style guides, especially the following projects.

- blader/humanizer
- conorbronsdon/avoid-ai-writing
- MrGeDiao/shuorenhua
- iKora128/stop-ai-slop-jp
- makotofalcon/humanizer-ja
- gonta223/humanizer-ja
- yisyeasy-crypto/academic-writing-dna-skill
- mizuamedesu/ReportSkills
- k16shikano's public technical-writing gist
- Wikipedia: Signs of AI writing / WikiProject AI Cleanup
- user-provided `predictable-reading-japanese` skill archive (2026-08-24; the archive did not include provenance or license metadata)

The package does not copy their rule text verbatim. The user-provided archive was used for conceptual comparison; selected ideas were rewritten and its examples were narrowed to preserve Humanizer JA Editor's fidelity contract. Humanizer JA Editor combines independently written instructions around five design goals:

1. semantic fidelity before style
2. scene-specific editing
3. writer-sample priority
4. false-positive and over-editing protection
5. predictable reader flow without invented facts or mechanical signposting

The linked projects retain their own copyrights and licenses. Review their repositories before redistributing any of their files or examples together with this package.

## Beginner explanation profile

The v0.4.0 beginner explanation profile was informed by the general teaching structures visible in the following user-provided public articles on 2026-08-31.

- Jay Alammar, [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- 3Blue1Brown, [But what is a Neural Network?](https://www.3blue1brown.com/lessons/neural-networks/)
- samwho.dev, [Reservoir Sampling](https://samwho.dev/reservoir-sampling/)
- Julia Evans, [What even is a container: namespaces and cgroups](https://jvns.ca/blog/2016/10/10/what-even-is-a-container/)
- MDN contributors, [インターネットの仕組み](https://developer.mozilla.org/ja/docs/Learn_web_development/Howto/Web_mechanics/How_does_the_Internet_work)
- Cloudflare, [機械学習における量子化とは？](https://www.cloudflare.com/ja-jp/learning/ai/what-is-quantization/)
- Amazon Web Services, [AWS の API を理解しよう ! 初級編](https://aws.amazon.com/jp/builders-flash/202209/way-to-operate-api/)

The profile independently restates broad patterns such as progressive disclosure, motivating a term through a problem, testing a naive approach against a constraint, separating a mental model from observed behavior, and pairing an analogy with its limits.
It does not copy article prose, diagrams, examples, code, numerical claims, product facts, personal anecdotes, catchphrases, or promotional language.
These articles remain under their respective copyrights and terms, and their links are provenance rather than runtime instructions or factual sources for a different subject.

## Guided tutorial profile

The v0.5.0 guided tutorial profile was informed by the general instructional structures visible in the following public resources, checked on 2026-08-31.

- cybozu developer network, [クイックスタート](https://cybozu.dev/ja/kintone/getting-started/quickstart/)
- LINE Developers, [応答ボットを作る](https://developers.line.biz/ja/docs/messaging-api/nodejs-sample/)
- Django Software Foundation, [はじめてのDjangoアプリ作成、その1](https://docs.djangoproject.com/ja/5.2/intro/tutorial01/)
- GitHub Docs, [Hello World](https://docs.github.com/ja/get-started/using-github/hello-world)
- Software Carpentry, [The Unix Shell](https://swcarpentry.github.io/shell-novice/)
- Google Codelabs, [Your first Flutter app](https://codelabs.developers.google.com/codelabs/flutter-codelab-first)
- Diátaxis, [Tutorials](https://diataxis.fr/tutorials/)

The profile independently restates broad patterns such as naming the starting state and goal, alternating an action with an observable checkpoint, keeping one primary path, placing known failure branches near their triggering step, and making completion conditional on a check.
It does not copy product-specific steps, commands, code, interface labels, sample output, versions, credentials, examples, personal voice, or claims that a reader has executed the tutorial.

## Troubleshooting profile

The v0.5.0 troubleshooting profile was informed by the general diagnostic and operational structures visible in the following public resources, checked on 2026-08-31.

- Google, [Effective Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/)
- Microsoft Learn, [Help us help you](https://learn.microsoft.com/en-us/dynamics365/get-started/support/support-scope-general)
- GitLab Docs, [Troubleshooting topic type](https://docs.gitlab.com/development/documentation/topic_types/troubleshooting/)
- Digital Agency of Japan, [DS-120 デジタル・ガバメント推進標準ガイドライン実践ガイドブック](https://www.digital.go.jp/assets/contents/node/basic_page/field_ref_resources/e2a06143-ed29-4f1d-9c31-0f06fca67afc/6f2f8a35/20230331_resources_standard_guidelines_guideline_05.pdf)
- Amazon Web Services, [テストとロールバックを自動化する](https://docs.aws.amazon.com/ja_jp/wellarchitected/latest/framework/ops_mit_deploy_risks_auto_testing_and_rollback.html)
- CyberAgent Developers Blog, [運用監視ワークショップ](https://developers.cyberagent.co.jp/blog/archives/29187/)
- Linc'well Engineering, [過去の障害対応記録からプロセスの改善に繋げる](https://zenn.dev/lincwell_inc/articles/analyse-software-incidents)

The profile independently restates broad patterns such as separating symptoms, observations, hypotheses, causal confidence, workarounds, fixes, live verification, and rollback, while preserving the authority boundary between diagnosis and mutation.
It does not copy organization-specific incident facts, commands, roles, taxonomies, service architecture, numerical claims, operational commitments, or authorial voice.

## Comparison and selection profile

The v0.5.0 comparison and selection profile was informed by the general decision structures visible in the following public resources, checked on 2026-08-31.

- UK Government, [Architectural Decision Record Framework](https://www.gov.uk/government/publications/architectural-decision-record-framework/architectural-decision-record-framework)
- HM Treasury, [Multi-Criteria Decision Analysis](https://www.gov.uk/government/publications/green-book-supplementary-guidance-multi-criteria-decision-analysis/use-of-multi-criteria-decision-analysis-in-options-appraisal-of-economic-cases)
- NASA, [Decision Analysis](https://www.nasa.gov/reference/6-8-decision-analysis/)
- Digital Agency of Japan, [生成AIの調達・利活用に係るガイドライン第2.0版](https://www.digital.go.jp/assets/contents/node/information/field_ref_resources/decb64eb-f26e-41cb-8d37-f3dd173108b8/59054b35/20260612_resources_standard_guidelines_guideline_01.pdf)
- Japan Council for Quality Health Care, [Minds診療ガイドライン作成マニュアル2020 ver.3.0 第6章](https://minds.jcqhc.or.jp/docs/methods/cpg-development/minds-manual/pdf/chap6_manual_2020ver.pdf)
- GOV.UK, [Managing technical lock-in in the cloud](https://www.gov.uk/guidance/managing-technical-lock-in-in-the-cloud)
- U.S. Government Accountability Office, [Technology Readiness Assessment Guide](https://www.gao.gov/products/gao-20-48g)

The profile independently restates broad patterns such as defining the decision context, filtering by hard requirements, applying shared criteria under comparable conditions, distinguishing unknown from failure, considering lifecycle and exit costs, and separating evidence certainty, recommendation strength, final decision, and execution authority.
It does not copy domain-specific criteria, scoring ranges, weights, maturity levels, candidate rankings, procurement rules, medical recommendations, product facts, or institutional wording.

All links in these three sections record design provenance. They are not runtime instructions, licenses for copied text, factual evidence for another subject, or proof that the resulting profile improves model output without separate evaluation.

## Japanese writing integration

v0.7.0 consolidates the `yasashii-nihongo-writer` and `japanese-tech-writing` guidance supplied during development. Overlapping guidance was rewritten into shared fidelity rules, independent reader conditions, conversation continuity, technical argumentation, and an optional manuscript style. These names identify earlier inputs to the design; the standalone skills and local compatibility entry are not distributed in this repository.

The easy-Japanese source skill identified the Agency for Cultural Affairs and Immigration Services Agency guides as design references:

- [やさしい日本語ガイドライン](https://www.bunka.go.jp/seisaku/kokugo_nihongo/kyoiku/pdf/92484001_01.pdf)
- [話し言葉のポイント](https://www.bunka.go.jp/seisaku/kokugo_nihongo/kyoiku/pdf/93832501_01.pdf)

Their administrative-information context is not a universal style requirement. The linked documents were not newly verified during this integration and are not copied or bundled. These provenance links do not supply facts for a user's target document.

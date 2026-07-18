# Three-behavior Humanizer comparison examples

This page applies all three user-facing behaviors to the same source passages:

1. Editorial Humanizer
2. Faithful Humanizer — Structural mode (default)
3. Faithful Humanizer — Conservative mode (opt-in)

The examples are style anchors, not golden outputs. Exact wording may vary. The
Faithful outputs must always preserve the same semantic invariants: propositions,
opinion ownership, attribution, modality, uncertainty, scope, quantification,
chronology, logical relationships, comparisons, exact anchors, meaningful order,
and register. Structural and Conservative differ only in intervention strategy.

Editorial is not automatically better because its output is shorter. It has
different authority: it may select, compress, reprioritize, or reorganize supplied
material within its factual-integrity safeguards. Neither skill may invent facts,
sources, experiences, or unsupported causal explanations.

The library spans personal opinion, academic limitations, product copy, community
programs, policy language, medical instructions, financial forecasts,
cybersecurity updates, technical procedures, customer support, fundraising, and
internal workplace communication.

## 1. Opinion and mixed stance

#### Source

> From my perspective, the redesign represents a meaningful improvement because it
> makes the settings easier to locate. At the same time, I remain concerned that
> the new navigation may confuse long-time users who are familiar with the current
> layout. That being said, the team can reduce this risk by keeping the old menu
> available until the end of September. Overall, I support the release, although I
> believe the transition requires careful communication.

#### Editorial Humanizer

> The redesign makes settings easier to find, but the new navigation may confuse
> long-time users. Keeping the old menu through the end of September would reduce
> that risk. I support the release, provided the transition is communicated
> carefully.

#### Faithful Structural

> The redesign is a meaningful improvement in my view because it makes the settings
> easier to find. I remain concerned about the new navigation, though: it may
> confuse long-time users who know the current layout. The team can reduce that
> risk by keeping the old menu available until the end of September. Despite that
> concern, I support the release, although I believe the transition requires
> careful communication.

#### Faithful Conservative

> I see the redesign as a meaningful improvement because it makes the settings
> easier to find. At the same time, I remain concerned that the new navigation may
> confuse long-time users familiar with the current layout. However, the team can
> reduce this risk by keeping the old menu available until the end of September. On
> balance, I support the release, although I believe the transition requires
> careful communication.

**Why they differ:** Editorial compresses and reprioritizes the position under its
broader authority. Both Faithful modes preserve the speaker's improvement claim,
reason, concern, uncertainty, affected users, mitigation, date, support, and
communication qualification. Structural changes the grammatical subject and
rebuilds the transition pattern; Conservative repairs the original sequence
locally.

## 2. Academic limitation and causal boundary

#### Source

> The findings suggest that remote work may improve retention for some employees.
> However, because the survey included only staff who had remained with the company
> for at least six months, the results should not be interpreted as evidence that
> remote work causes lower turnover. Taken together, these observations highlight
> the importance of conducting further research across a wider range of roles and
> tenure levels.

#### Editorial Humanizer

> Remote work may improve retention for some employees, but this survey cannot
> establish that it reduces turnover: it included only staff who had remained with
> the company for at least six months. Research across a wider range of roles and
> tenure levels is needed.

#### Faithful Structural

> The findings suggest that remote work may improve retention for some employees.
> The survey, however, included only staff who had remained with the company for at
> least six months. Its results should therefore not be interpreted as evidence
> that remote work causes lower turnover. Taken together, these observations show
> why further research across a wider range of roles and tenure levels is important.

#### Faithful Conservative

> The findings suggest that remote work may improve retention among some employees.
> However, because the survey included only staff who had remained with the company
> for at least six months, the results should not be taken as evidence that remote
> work causes lower turnover. Together, these observations highlight the importance
> of further research across a wider range of roles and tenure levels.

**Why they differ:** Editorial compresses the evidence chain and recommendation.
Both Faithful modes preserve `suggest`, `may`, `some employees`, the survey's
six-month inclusion limit, the non-causal interpretation, and the research
recommendation. Structural separates the limitation from the inference and moves
the qualification closer to the result it governs. Conservative keeps the original
sentence architecture.

## 3. Product and technical scope

#### Source

> Atlas Notes provides offline access to saved documents, which enables travelers
> to review project files without an internet connection, while also allowing
> administrators to revoke access after a device has been lost, thereby helping
> organizations balance convenience with security.

#### Editorial Humanizer

> Atlas Notes keeps saved documents available offline. Administrators can revoke
> access after a device is lost.

#### Faithful Structural

> Saved documents remain available offline in Atlas Notes, so travelers can review
> project files without an internet connection. If a device is lost, administrators
> can revoke its access. Together, these features help organizations balance
> convenience with security.

#### Faithful Conservative

> Atlas Notes provides offline access to saved documents, so travelers can review
> project files without an internet connection. At the same time, it allows
> administrators to revoke access after a device has been lost, helping organizations
> balance convenience with security.

**Why they differ:** Editorial selects the two concrete controls and omits the use
case and balancing claim. The Faithful modes retain offline availability, the
traveler example, administrative revocation after loss, and the convenience-security
relationship. Structural turns the overloaded source into three meaning-driven
sentences; Conservative uses a local two-sentence repair. A Structural rewrite must
not say that Atlas Notes "gives travelers offline access," which would narrow a
generally available feature to one use case.

## 4. Multi-sentence community program

#### Source

> First and foremost, the community program is designed to provide weekly tutoring
> for students in grades 7 and 8. In addition, the program offers monthly workshops
> for parents who want help understanding the school application process. Moreover,
> volunteer mentors may meet individually with some students when additional
> support is needed. In conclusion, these combined services demonstrate the
> program's ongoing commitment to supporting both students and families.

#### Editorial Humanizer

> The community program provides weekly tutoring for students in grades 7 and 8,
> monthly school-application workshops for parents, and individual volunteer
> mentoring for some students who need additional support.

#### Faithful Structural

> Weekly tutoring for students in grades 7 and 8 sits at the center of the community
> program. The program also offers monthly workshops for parents who want help
> understanding the school application process. When additional support is needed,
> some students may meet one-on-one with volunteer mentors. Together, these services
> show the program's continuing commitment to students and families.

#### Faithful Conservative

> The community program is designed first and foremost to provide weekly tutoring
> for students in grades 7 and 8. It also offers monthly workshops for parents who
> want help understanding the school application process. When additional support
> is needed, volunteer mentors may also meet individually with some students.
> Together, these services demonstrate the program's ongoing commitment to
> supporting both students and families.

**Why they differ:** Editorial compresses the paragraph into a service summary and
does not retain the closing commitment claim as a separate proposition. Both
Faithful modes preserve weekly and monthly frequency, the student grades, parent
audience and workshop purpose, optional individual mentoring for some students,
the support condition, and the continuing commitment to students and families.
Structural changes subjects and information flow; Conservative stays close to the
existing paragraph. Neither mode should replace `first and foremost` with `primary
purpose` unless the source supports that stronger formal hierarchy.

## 5. Policy deadline and documented exception

#### Source

> Employees must submit travel expense reports within 30 calendar days after
> returning from a trip. However, if the finance system is unavailable during
> that period, employees may submit the report within five business days after
> service is restored. Managers are required to document the outage, and late
> submissions without that documentation will not be reimbursed.

#### Editorial Humanizer

> Employees must submit travel expense reports within 30 calendar days of returning
> from a trip.
> If the finance system is unavailable during that period, employees may submit
> within five business days after service is restored, provided a manager documents
> the outage. Undocumented late submissions will not be reimbursed.

#### Faithful Structural

> Travel expense reports are due within 30 calendar days after employees return
> from a trip. If the finance system is unavailable during that window, employees
> may instead file within five business days after service is restored. Managers
> must document the outage; without that documentation, late submissions will not
> be reimbursed.

#### Faithful Conservative

> Employees must submit travel expense reports within 30 calendar days of returning
> from a trip. However, if the finance system is unavailable during that period,
> employees may submit the report within five business days after service is
> restored. Managers must document the outage, and late submissions without that
> documentation will not be reimbursed.

**Why they differ:** Editorial tightens the policy and combines the exception with
its documentation requirement. Both Faithful modes
retain the employee obligation, 30-calendar-day deadline, system-unavailability
condition, five-business-day extension, restoration trigger, manager documentation,
and reimbursement consequence. Structural changes subjects and joins the final
condition to its consequence; Conservative makes localized wording changes.

## 6. Medical instruction with time and escalation conditions

#### Source

> After starting this medication, some patients may experience mild dizziness
> during the first 48 hours. For this reason, patients should avoid driving until
> they know how the medication affects them. If dizziness is severe, lasts beyond
> 48 hours, or is accompanied by fainting, patients should contact the clinic
> immediately.

#### Editorial Humanizer

> Some patients may experience mild dizziness during the first 48 hours after
> starting this medication. Patients should avoid driving until they know how it
> affects them. They should contact the clinic immediately if the dizziness is
> severe, lasts beyond 48 hours, or is accompanied by fainting.

#### Faithful Structural

> During the first 48 hours after starting this medication, some patients may
> experience mild dizziness. Patients should avoid driving until they know how the
> medication affects them. Patients should contact the clinic immediately for
> severe dizziness, dizziness lasting beyond 48 hours, or dizziness accompanied by
> fainting.

#### Faithful Conservative

> Some patients may experience mild dizziness during the first 48 hours after
> starting this medication. For that reason, patients should avoid driving until
> they know how the medication affects them. If the dizziness is severe, continues
> beyond 48 hours, or occurs with fainting, patients should contact the clinic
> immediately.

**Why they differ:** Editorial uses direct patient-facing instructions while
preserving the source's uncertainty and escalation criteria. Both Faithful modes
retain `some patients`, `may`, mild dizziness, the first 48 hours, the driving
precaution and its endpoint, all three escalation conditions, and `immediately`.
Structural recasts the conditional list as a subject; Conservative keeps the
original condition-led architecture. Medical text still requires qualified human
review.

## 7. Financial forecast with assumptions and exclusions

#### Source

> Management currently expects Q4 revenue to be between $18 million and $21
> million, assuming renewal rates remain near current levels. This range does not
> include revenue from the proposed Northstar acquisition, which has not yet
> closed. If renewal rates decline materially, actual revenue could fall below the
> range.

#### Editorial Humanizer

> Management currently expects Q4 revenue of $18 million to $21 million if renewal rates
> remain near current levels. The forecast excludes the proposed Northstar
> acquisition, which has not closed, and revenue could fall below the range if
> renewal rates decline materially.

#### Faithful Structural

> Assuming renewal rates remain near current levels, management currently expects
> Q4 revenue of $18 million to $21 million. Revenue from the proposed Northstar
> acquisition is excluded because the transaction has not yet closed. A material
> decline in renewal rates could put actual revenue below the expected range.

#### Faithful Conservative

> Management currently expects Q4 revenue of between $18 million and $21 million,
> provided renewal rates remain near current levels. The range excludes revenue
> from the proposed Northstar acquisition, which has not yet closed. If renewal
> rates decline materially, actual revenue could fall below that range.

**Why they differ:** Editorial consolidates the forecast's exclusions and downside
condition. Both Faithful modes retain management attribution, `currently`, Q4, the
$18 million–$21 million range, the renewal-rate assumption, the excluded proposed
acquisition, its unclosed status, and the possibility of falling below the range.
Structural leads with the governing assumption; Conservative preserves the
original progression.

## 8. Cybersecurity incident chronology and unresolved status

#### Source

> At 14:20 UTC on 6 March, monitoring detected repeated failed sign-in attempts
> against 27 customer accounts. The security team blocked the originating IP
> addresses at 14:37 UTC and forced password resets for the affected accounts. The
> investigation has not found evidence of successful access, but log review
> remains ongoing.

#### Editorial Humanizer

> Monitoring detected repeated failed sign-in attempts against 27 customer accounts
> at 14:20 UTC on 6 March. At 14:37 UTC, the security team blocked the originating
> IP addresses and forced password resets. The investigation has found no evidence
> of successful access, and log review is
> ongoing.

#### Faithful Structural

> Repeated failed sign-in attempts against 27 customer accounts were detected by
> monitoring at 14:20 UTC on 6 March. At 14:37 UTC, the security team blocked the
> originating IP addresses and forced password resets for the affected accounts.
> Log review remains ongoing, and the investigation has not found evidence of
> successful access.

#### Faithful Conservative

> At 14:20 UTC on 6 March, monitoring detected repeated failed sign-in attempts
> against 27 customer accounts. At 14:37 UTC, the security team blocked the
> originating IP addresses and forced password resets for the affected accounts.
> The investigation has found no evidence of successful access, but log review is
> still ongoing.

**Why they differ:** Editorial streamlines the incident update while retaining its
facts and unresolved status. Both Faithful modes preserve the two timestamps and
their order, date, 27-account scope, failed-attempt status, blocked IP addresses,
forced resets, absence of found evidence, and ongoing review. Structural changes
the grammatical subjects and final clause order without implying that the
investigation is complete; Conservative stays close to the chronology-led source.

## 9. Technical upgrade procedure with exact anchors

#### Source

> Before upgrading the controller to version 4.8.2, export the current
> configuration to `/var/backups/controller.json` and verify that the file is at
> least 1 KB. Run `ctl upgrade --version 4.8.2` only after both steps succeed. If
> the command returns exit code 23, do not retry; restore version 4.7.9 and contact
> platform support.

#### Editorial Humanizer

> Export the controller configuration to `/var/backups/controller.json` and confirm
> that the file is at least 1 KB. Only then should you run
> `ctl upgrade --version 4.8.2`. If it returns exit code 23, do not retry: restore
> version 4.7.9 and contact platform support.

#### Faithful Structural

> Export the current configuration to `/var/backups/controller.json` before
> upgrading the controller to version 4.8.2. Verify that the file is at least 1 KB,
> then run `ctl upgrade --version 4.8.2` only after both steps have succeeded. An
> exit code of 23 means do not retry; restore version 4.7.9 and contact platform
> support.

#### Faithful Conservative

> Before upgrading the controller to version 4.8.2, export the current configuration
> to `/var/backups/controller.json` and confirm that the file is at least 1 KB. Run
> `ctl upgrade --version 4.8.2` only after both steps succeed. If the command returns
> exit code 23, do not retry; restore version 4.7.9 and contact platform support.

**Why they differ:** Editorial removes repeated version wording while retaining the
operational sequence. Both Faithful modes preserve every command, path, version,
size threshold, prerequisite, exit code, prohibition, rollback target, and support
step. Structural redistributes the prerequisites across sentences; Conservative
changes only local wording. None may reorder the upgrade, verification, or rollback
sequence.

## 10. Customer support with pending-payment uncertainty

#### Source

> Thank you for contacting us about the duplicate charge. We have confirmed that
> the second payment is still pending and has not been captured. Most pending
> authorizations disappear within 3–5 business days, but your bank may take longer.
> If the charge posts, reply to this email with the transaction date and we will
> investigate within two business days.

#### Editorial Humanizer

> Thank you for contacting us about the duplicate charge. We confirmed that the
> second payment is still pending and has not been captured. Most pending authorizations
> disappear within 3–5 business days, although your bank may take longer. If the
> charge posts, reply with the transaction date and we will investigate within two
> business days.

#### Faithful Structural

> Thank you for contacting us about the duplicate charge. The second payment remains
> pending; we confirmed that it has not been captured. Although most pending
> authorizations disappear within 3–5 business days, your bank may take longer. If
> the charge posts, reply to this email with the transaction date. We will then
> investigate within two business days.

#### Faithful Conservative

> Thank you for contacting us about the duplicate charge. We confirmed that the
> second payment is still pending and has not been captured. Most pending
> authorizations disappear within 3–5 business days, though your bank may take
> longer. If the charge posts, reply to this email with the transaction date, and
> we will investigate within two business days.

**Why they differ:** The source is already fairly natural, so all three outputs
converge more than they do in formulaic examples. Both Faithful modes retain the
thanks, second-payment status, pending-versus-captured distinction, `most`, the
3–5-business-day norm, bank uncertainty, posting condition, requested transaction
date, and two-business-day investigation commitment. Structural safely splits the
conditional response; Conservative makes only local changes.

## 11. Fundraising appeal with a promotional belief claim

#### Source

> Because the Riverside Learning Fund covers transportation, meals, and course
> materials, every $75 donation allows one student to attend a full Saturday
> workshop at no cost to their family. Contributions received by December 15 will
> also be matched by the Lorne Foundation, up to a total of $20,000. We believe
> this support can help more students participate consistently.

#### Editorial Humanizer

> Every $75 donation to the Riverside Learning Fund covers transportation, meals,
> and course materials for one student to attend a full Saturday workshop at no
> cost to their family. The Lorne Foundation will match contributions received by
> December 15, up to $20,000.

#### Faithful Structural

> Every $75 donation allows one student to attend a full Saturday workshop at no
> cost to their family because the Riverside Learning Fund covers transportation,
> meals, and course materials. The Lorne Foundation will also match contributions
> received by December 15, up to a total of $20,000. We believe this support can
> help more students participate consistently.

#### Faithful Conservative

> The Riverside Learning Fund covers transportation, meals, and course materials,
> so every $75 donation allows one student to attend a full Saturday workshop at
> no cost to their family. Contributions received by December 15 will also be
> matched by the Lorne Foundation, up to a total of $20,000. We believe this
> support can help more students participate consistently.

**Why they differ:** Editorial uses its selection authority to omit the broad final
belief claim while retaining the concrete donation and match terms. Both Faithful
modes must preserve the three covered costs, `every $75`, one student, the full
Saturday workshop, no family cost, December 15, the Lorne Foundation, the $20,000
cap, the organization's belief, and `can`. Structural changes the causal framing;
Conservative stays close to the source.

## 12. Workplace update with criticism and early evidence

#### Source

> To be candid, I was disappointed that the pilot launched before the support team
> completed training. Even so, the first-week response time was 12% faster than in
> May, and three team leads told me the new queue is easier to manage. I do not
> think those early results justify expanding the pilot until the training gaps
> are closed.

#### Editorial Humanizer

> I was disappointed that the pilot launched before the support team completed training.
> First-week response time was 12% faster than in May, and three team leads told me
> the new queue is easier to manage. Even with those early results, I do not think
> they justify expanding the pilot until the training gaps are closed.

#### Faithful Structural

> I was disappointed that the pilot launched before the support team completed
> training. Still, first-week response time was 12% faster than in May, and three
> team leads told me that the new queue is easier to manage. In my view, those early
> results do not justify expanding the pilot until the training gaps are closed.

#### Faithful Conservative

> Candidly, I was disappointed that the pilot launched before the support team
> completed training. Even so, first-week response time was 12% faster than in May,
> and three team leads told me the new queue is easier to manage. I do not believe
> those early results justify expanding the pilot until the training gaps are
> closed.

**Why they differ:** Editorial removes formulaic framing and sharpens the progression
while preserving the speaker's ownership of both judgments. Both Faithful modes
retain the speaker's disappointment, launch-before-training chronology, 12%
comparison with May, three-lead attribution, easier-management claim, negative
judgment about expansion, `early` limitation, and training-gap condition.
Structural removes formulaic framing and restates opinion ownership explicitly;
Conservative makes localized changes.

## Selection rule

Choose Editorial when the user authorizes content selection, compression,
reprioritization, stronger voice, or argument restructuring. Choose Faithful when
every substantive element must survive. Within Faithful, Structural is the default;
choose Conservative only when the user explicitly asks for minimal, light-touch,
stay-close, copyedit-only, or structure-preserving intervention.

High-stakes or scientific register strengthens the preservation review but does
not silently switch modes. Detector evasion is not an objective in any behavior.

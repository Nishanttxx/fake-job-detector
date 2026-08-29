# Visual verification notes

The desktop screening view preserves the existing editorial layout and now shows a visible character counter and minimum-length hint below the job description field. The form footer remains aligned and the primary button is still clear at the 1280px viewport.

The narrow mobile view remains usable at 390px: navigation compresses into a horizontal workspace bar, the input card stacks fields vertically, the character counter remains readable, and the result panel follows the form without horizontal overflow. The loading panel and inline form-error classes are responsive and include a reduced-motion fallback.

The live browser preview accepted the deliberately short input `urgent hire` and exposed the enabled Run screening control. The next interaction will submit it to verify the detailed validation alert and the fact that no model request is made for invalid input.

Live browser verification exercised the invalid-description state: submitting `urgent hire` displayed the inline alert “We need a little more detail” with the exact 11-character guidance, kept the result panel empty, and returned no model score. The browser then accepted a 358-character realistic posting with the screening action enabled; the next interaction will verify the loading and successful result states.

Live browser verification exercised the success state with a 358-character realistic posting: the result panel returned Legitimate with 9% fake risk, 91% legitimate probability, no matched rule-based warning signals, and the model/version disclaimer. A temporary 1.5-second request delay was then installed in the browser only to make the animated loading state observable in the next capture.

The live browser flow directly exercised the animated state after a temporary 1.5-second request delay: the result panel showed “Screening in progress,” the pulsing radar orb, “Reading the signal…,” staged progress labels, and the button label “Analyzing posting…”. After the request resolved, the same panel returned the successful Legitimate / 9% fake-risk result. This confirms the loading transition and the resolved success state in the browser.

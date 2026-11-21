; Parameter atoms begin with @. The finite ground inventory instantiates them
; from the ontology, the selected frame's controller, or a typed tense wrapper.
(recipe noun @symbol)
(recipe name (fn k R (k @symbol)))
(recipe det (fn n R (fn k R (@quant (fn x E (@join (n x) (k x)))))))
(recipe iv (fn qs Q (fn k K (qs (fn s E (ExistsV (fn e V
  (And (@pred e) (And (Agent e s) (@tense e (k e)))))))))))
(recipe tv.subject-wide (fn qo Q (fn qs Q (fn k K
  (qs (fn s E (qo (fn o E (ExistsV (fn e V
    (And (@pred e) (And (Agent e s) (And (Theme e o) (@tense e (k e)))))))))))))))
(recipe tv.object-wide (fn qo Q (fn qs Q (fn k K
  (qo (fn o E (qs (fn s E (ExistsV (fn e V
    (And (@pred e) (And (Agent e s) (And (Theme e o) (@tense e (k e)))))))))))))))
(recipe control (fn qr Q (fn vp VP (fn qs Q (fn k K
  (qs (fn s E (qr (fn r E (ExistsV (fn e V
    (And (@pred e) (And (Agent e s) (And (Recipient e r)
      (And (Content e (Box (vp (fn c R (c @controller)) (fn b V Top))))
           (@tense e (k e)))))))))))))))))
(recipe manner (fn vp VP (fn qs Q (fn k K (vp qs (fn e V (And (Quick e) (k e))))))))
(recipe infinitive (fn vp VP vp))
(recipe negation (fn vp VP (fn qs Q (fn k K
  (qs (fn s E (Not (vp (fn c R (c s)) (fn e V (And (Past e) (k e)))))))))))
(recipe not-every (fn n R (fn vp VP (fn k K
  (Not (vp (fn c R (ForallE (fn s E (Implies (n s) (c s))))) k))))))

READ V2

V2/Unified/Keyv2.all
0 - useless
1 - useless
2 - short descr
3 - longer descr
4 - longest descr
5 - term id
6 - EN?
7 - code with trailing full stops
8 - 0?

seems that some codes (e.g. C10E) have the primary and a secondary description the same (with the same term code)
	This is true in TRUD, maybe not in the file


CTV3

/V3/Terms.v3
0 - Term ID
1 - Whether the (associated code/actual term)? is O(ptional) or C(urrent)
	Think it is the term. For example, code m48h. is optional and is associtated with
	term y00uy - Diprosone 0.05% cream 100g. However, the term is marked as C(urrent)
2 - short descr
3 - longer descr
4 - longest descr

/V3/V3hier.v3
0 - Child code ID
1 - Parent code ID
2 - ??

/V3/Redun.map
0 - New code ID
1 - Old code ID

/V3/Descrip.v3
0 - Code ID
1 - Term ID
2 - P(rimary) or S(econdary) (I believe there is no other choice)






/V3/Dcf.v3
Not really sure (maybe something to do with the redundancies...), but seems not useful

/V3/Keys.v3
No idea and giving up

/V3/Template.v3
Seems to be not important for what I'm doing
Type 1 diabtetes was linked to terms like episodiciteis and severities

/V3/Concept.v3
I think this records the type of the code (so not really needed...)
Ya0rM|C|Read thesaurus concept type||
Ya0rN|C|Temporary type||
Ya0rO|C|Type type||
Ya0rP|C|Prevention type||
Ya0rQ|C|Context-dependent type||
Ya0rR|C|Occupation type||
Ya0rS|C|Administration type||
Ya0rT|C|Findings category type||
Ya0rU|C|Attribute type||
Ya0rV|C|Value type||
Ya0rW|C|Clinical findings type||
Ya0rX|C|Procedure type||
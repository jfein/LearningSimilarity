from util import SourceArticles, cosine
import os, re
import random, math, json


THRESHOLDS = [x / 200.0 for x in xrange(0, 201, 1)]

positives = []
negatives = []

positives += [(0.6487360891749189, 0.8824663667365773, 0.7107058383910636, 0.6635875988509391, 0.6280748669016404, 0.6423696521692562), (0.6496696969064235, 0.8782269103659429, 0.7107058383910636, 0.7170958877293138, 0.6344414456900922, 0.678320319995395), (0.6878403500423893, 0.8670765108841084, 0.6635875988509391, 0.7170958877293138, 0.6249218712239135, 0.6617965359385753), (0.4624157782918783, 0.7452198208413986, 0.6255966228503951, 0.6121695886533823, 0.5057770851335682, 0.4794653429751601), (0.497711658470212, 0.7886465527226248, 0.6255966228503951, 0.6086842513094751, 0.538267624484673, 0.5051096306810103), (0.7460130026238062, 0.8665556800811062, 0.6121695886533823, 0.6086842513094751, 0.5684705349845243, 0.5488247504612558)]
positives += [(0.647291482137277, 0.8895560424980387, 0.776801858523347, 0.7774741131618564, 0.7408478058627327, 0.7354994276761547), (0.6466794458573007, 0.9057828287038041, 0.776801858523347, 0.7940844788408193, 0.7421771979021426, 0.7573969454794534), (0.6666677258083437, 0.8970987428048218, 0.7774741131618564, 0.7940844788408193, 0.7381254768878805, 0.7340346772314887), (0.5260810611221026, 0.8478258165974705, 0.7075671371151491, 0.6969038057877495, 0.6296866297586085, 0.6134440641394839), (0.5238095238095238, 0.828163214979014, 0.7075671371151491, 0.6930715581490473, 0.5928366610618397, 0.6047192919778965), (0.6497771746437302, 0.850481928436394, 0.6969038057877495, 0.6930715581490473, 0.6102314230108731, 0.6480333785965283)]
positives += [(0.5339589873511373, 0.8336845768806802, 0.6956801020311386, 0.6467018764704189, 0.572936095942293, 0.5711498619767319), (0.5433916725566573, 0.8404657230031916, 0.6956801020311386, 0.6775392558297774, 0.5828579464698823, 0.5887633992205525), (0.607714915247248, 0.8762075100844487, 0.6467018764704189, 0.6775392558297774, 0.5854586697706474, 0.6005576198590405), (0.6234686685453402, 0.8889043837789099, 0.7466468968155106, 0.7419421093686138, 0.7329392917329719, 0.6806408945176673), (0.6386323824202593, 0.8802910795574582, 0.7466468968155106, 0.7397063835195885, 0.7155850498184912, 0.6947403022089191), (0.7028166928018867, 0.9136026543139961, 0.7419421093686138, 0.7397063835195885, 0.70352743738456, 0.7196383255875326)]
positives += [(0.6823745121128986, 0.8813249314569322, 0.6964953333168901, 0.720146288143793, 0.6334635047558711, 0.691998823397898), (0.6846689895470385, 0.8839873319255612, 0.6964953333168901, 0.6827206123863477, 0.6427286099871474, 0.6494444714960971), (0.8499140342684951, 0.912251160676685, 0.720146288143793, 0.6827206123863477, 0.6924978221276904, 0.6515624620346103), (0.7031070368223251, 0.8710412012232498, 0.7032564275931688, 0.7341320530268819, 0.6729549381321952, 0.6818811356975933), (0.7058871234963557, 0.886374677490881, 0.7032564275931688, 0.7135417368087881, 0.6713852499743749, 0.6696691695954767), (0.8812068330682251, 0.9157874662170095, 0.7341320530268819, 0.7135417368087881, 0.7085613605169461, 0.7003631004835533)]
positives += [(0.7446796578007466, 0.9584706181157268, 0.7556896053754729, 0.7515747116671027, 0.7592080540201257, 0.7271260397127265), (0.7348107404865382, 0.9564726259673171, 0.7556896053754729, 0.7641785002598394, 0.7486018784115454, 0.7436498194863002), (0.8731157670966831, 0.9765526852502477, 0.7515747116671027, 0.7641785002598394, 0.73470075800752, 0.7625634185211155), (0.7178016925346351, 0.8909077499705753, 0.7930582761883025, 0.790994062113376, 0.7520724775150325, 0.7397404841969955), (0.7440990428564852, 0.9014151788929499, 0.7930582761883025, 0.7833292733785799, 0.7585930463593167, 0.7484194758515497), (0.8177769206412799, 0.9013411453323233, 0.790994062113376, 0.7833292733785799, 0.7458439840193375, 0.7536693654376287)]
positives += [(0.486013986013986, 0.7777427261642591, 0.668343867188534, 0.6505436778839966, 0.5733101818795039, 0.5276799133433931), (0.4897017574364857, 0.8084846770763489, 0.668343867188534, 0.6854229483444723, 0.577680500509217, 0.5826952292225587), (0.5569495339858622, 0.841291997128437, 0.6505436778839966, 0.6854229483444723, 0.5596954288868877, 0.6020790606404619), (0.6132239781768964, 0.8374861572535991, 0.7432706444625632, 0.7354743878758024, 0.6838312966008158, 0.6408243277086623), (0.6516811486308821, 0.86547751429841, 0.7432706444625632, 0.7427836890339116, 0.6789846094858638, 0.6565223725452912), (0.7304745310495808, 0.8749484495958127, 0.7354743878758024, 0.7427836890339116, 0.6826465560568121, 0.6937941625051128)]
positives += [(0.5342155309358262, 0.8066403157030636, 0.7017120678707036, 0.6965397386978371, 0.5908803860229742, 0.6081503078529631), (0.547491752826971, 0.7917718311126538, 0.7017120678707036, 0.7226157892354608, 0.5974880234974036, 0.6467984737289282), (0.7439868104618774, 0.8399184687416319, 0.6965397386978371, 0.7226157892354608, 0.6475752359274597, 0.6620103388270776), (0.4927827345595468, 0.8156584021697786, 0.7348137555143053, 0.7124026798147473, 0.6286333028404706, 0.6145941492458196), (0.4818013588264925, 0.8285521219479982, 0.7348137555143053, 0.7350654022122209, 0.660684635966167, 0.6411324452364905), (0.5555898522840232, 0.8215681839113498, 0.7124026798147473, 0.7350654022122209, 0.6458553209366121, 0.6198640628147383)]
positives += [(0.5934967195414262, 0.8444750044508104, 0.7411065250980304, 0.8261453701278594, 0.6901708273130019, 0.702340354305955), (0.6097569036384516, 0.8336985653801442, 0.7411065250980304, 0.8364946555349619, 0.6819591916280547, 0.7108449801905881), (0.6461038961038961, 0.8624664991350043, 0.8261453701278594, 0.8364946555349619, 0.7441035720859007, 0.7554553168498489), (0.6024693825640112, 0.8162711028785911, 0.7410156088435996, 0.7355308165680117, 0.6370944273544782, 0.6351487366379901), (0.6228492178250125, 0.8097271116850211, 0.7410156088435996, 0.7586889487137669, 0.652566634004302, 0.6560066367695055), (0.6972923197030648, 0.8793137073979941, 0.7355308165680117, 0.7586889487137669, 0.6628991414673644, 0.6747942165222449)]
positives += [(0.7085170531485793, 0.868190174650813, 0.7440800469794578, 0.7420729249905863, 0.6783679072854439, 0.735516150762659), (0.735889486049104, 0.8835965122793162, 0.7440800469794578, 0.7323146069871628, 0.6867104695147541, 0.697770085470857), (0.7937704085584172, 0.9164556465241552, 0.7420729249905863, 0.7323146069871628, 0.7196584606775293, 0.6923478664222882), (0.7866728552949309, 0.8777825368538837, 0.7847725743451999, 0.7254586098301649, 0.7246340064279322, 0.6946498966243119), (0.7839572555045354, 0.8654422721829905, 0.7847725743451999, 0.7484790057970322, 0.7397855062705829, 0.7122884755774045), (0.8897069123202924, 0.9291629522566373, 0.7254586098301649, 0.7484790057970322, 0.7022104703360903, 0.7388599227329182)]
positives += [(0.5703404277931892, 0.7718074375689319, 0.7027467944112618, 0.7548116103247172, 0.5840085625899338, 0.6126220223980028), (0.5717877912965627, 0.7593269725957941, 0.7027467944112618, 0.7520529463912045, 0.5940627832858221, 0.6068290251087122), (0.6726566043238954, 0.8279558437065956, 0.7548116103247172, 0.7520529463912045, 0.6549617551116405, 0.6516646543880795), (0.5682895542659794, 0.7987558235607156, 0.6880864628082014, 0.698875869229562, 0.5733119300874632, 0.59874823225429), (0.5467528502397432, 0.7914543654021237, 0.6880864628082014, 0.7015757432670715, 0.5810394774235028, 0.5765952543156625), (0.5490057121317127, 0.8146297703234721, 0.698875869229562, 0.7015757432670715, 0.6049611096008091, 0.5805270461211829)]
positives += [(0.5412294272573258, 0.830115870910656, 0.7084116158505713, 0.6682986432544882, 0.60681915988126, 0.5973799112060947), (0.541935919546824, 0.8338180430536891, 0.7084116158505713, 0.6954486466959, 0.6076350367782926, 0.6186133296557423), (0.5978098087168854, 0.870005684339116, 0.6682986432544882, 0.6954486466959, 0.6089574424485529, 0.6119988557220793), (0.5550493399120858, 0.848157261138144, 0.69950674043549, 0.6880543181144262, 0.6178428232041618, 0.6151638690888858), (0.564581917198975, 0.8350986058644082, 0.69950674043549, 0.6786681117483413, 0.5952486236572233, 0.6000142692367167), (0.6510213735576036, 0.8421149043107043, 0.6880543181144262, 0.6786681117483413, 0.6032388955911945, 0.6226391897796626)]

negatives += [(0.3232093190368893, 0.6124574851830964, 0.7107058383910636, 0.6255966228503951, 0.33443737506095617, 0.435900260714209), (0.34687734722869706, 0.586096492076066, 0.7107058383910636, 0.6121695886533823, 0.33415764591896413, 0.4293832972403134), (0.35804243639393135, 0.6288777114822949, 0.7107058383910636, 0.6086842513094751, 0.36155848575199484, 0.44028864495049397), (0.3359449608462986, 0.599631872612748, 0.6635875988509391, 0.6255966228503951, 0.31583833815959844, 0.42703133802311477), (0.35799391787126217, 0.5850815090757313, 0.6635875988509391, 0.6121695886533823, 0.33215556428663323, 0.4333497018555077), (0.37106180177913106, 0.6229623053567221, 0.6635875988509391, 0.6086842513094751, 0.3575763003374145, 0.44938419330370044), (0.34380885932169214, 0.5970611389420867, 0.7170958877293138, 0.6255966228503951, 0.3484159757364882, 0.43735268535962435), (0.34302658559061483, 0.5731455272731265, 0.7170958877293138, 0.6121695886533823, 0.34541542633714384, 0.41685555558638265), (0.35948713265805526, 0.621975628722795, 0.7170958877293138, 0.6086842513094751, 0.37725334449028874, 0.43036351543506224)]
negatives += [(0.36129784186475644, 0.6797122054668632, 0.776801858523347, 0.7075671371151491, 0.4684818945642521, 0.49895253336292944), (0.3731440871284145, 0.672509535742359, 0.776801858523347, 0.6969038057877495, 0.4282575405542401, 0.44518431821822557), (0.3661366522468737, 0.6515498313023304, 0.776801858523347, 0.6930715581490473, 0.42599866954535265, 0.45942512487573633), (0.38890641478088145, 0.6723671980417234, 0.7774741131618564, 0.7075671371151491, 0.46124279424980447, 0.4782624337334784), (0.3748195862111104, 0.6503497967884564, 0.7774741131618564, 0.6969038057877495, 0.425602340905486, 0.4584847861854557), (0.3628708388959689, 0.6361003739838272, 0.7774741131618564, 0.6930715581490473, 0.41607119744326454, 0.46931099780798546), (0.3896002715587342, 0.6900051724063166, 0.7940844788408193, 0.7075671371151491, 0.4699094160133993, 0.49492495972914774), (0.3591627316465866, 0.6700379048489761, 0.7940844788408193, 0.6969038057877495, 0.44430618235421826, 0.45933177631575733), (0.3814496382625264, 0.6571075005026981, 0.7940844788408193, 0.6930715581490473, 0.42837160672416297, 0.4826166164898103)]
negatives += [(0.3818142573033137, 0.6841250201640235, 0.6956801020311386, 0.7466468968155106, 0.44016641024148795, 0.5311739131849627), (0.4009437375899206, 0.6619577796171899, 0.6956801020311386, 0.7419421093686138, 0.4662033966026482, 0.5314760674207321), (0.3989039126792342, 0.6759383338296926, 0.6956801020311386, 0.7397063835195885, 0.46925049935975344, 0.5154106078537981), (0.3673764884839823, 0.6971433819198405, 0.6467018764704189, 0.7466468968155106, 0.42235037553725535, 0.5141557531011143), (0.39078788547932936, 0.6689632616428427, 0.6467018764704189, 0.7419421093686138, 0.423654765303163, 0.5342728509881735), (0.3670832097648252, 0.6747496158334056, 0.6467018764704189, 0.7397063835195885, 0.4157781570894834, 0.5199776505643595), (0.42159364419800893, 0.6896117707185224, 0.6775392558297774, 0.7466468968155106, 0.4282466964416218, 0.5358013239633218), (0.41470910296471625, 0.6833272399765314, 0.6775392558297774, 0.7419421093686138, 0.44938202507848807, 0.545448903658225), (0.40847531545166016, 0.6836815554850113, 0.6775392558297774, 0.7397063835195885, 0.43413175441853835, 0.5279708082642756)]
negatives += [(0.3429643359636722, 0.5861234099220053, 0.6964953333168901, 0.7032564275931688, 0.36874969431155497, 0.4444130990837147), (0.33754223048382553, 0.6195449156235356, 0.6964953333168901, 0.7341320530268819, 0.392136277430464, 0.4499877628236334), (0.3460204125086948, 0.5950652651467649, 0.6964953333168901, 0.7135417368087881, 0.3804248100613724, 0.46659176092285853), (0.33640582991329326, 0.6169794505484789, 0.720146288143793, 0.7032564275931688, 0.40386056328557635, 0.46615764904702317), (0.35770787733746284, 0.6354539301823972, 0.720146288143793, 0.7341320530268819, 0.42846331305810964, 0.4643555055214899), (0.3538087494352579, 0.607076095375682, 0.720146288143793, 0.7135417368087881, 0.4122896022791369, 0.48724523147528237), (0.33760551821423984, 0.5994162696557839, 0.6827206123863477, 0.7032564275931688, 0.3926847657475991, 0.45471192910092595), (0.34997799687007175, 0.6280797411338221, 0.6827206123863477, 0.7341320530268819, 0.3997064758364575, 0.4646139109816927), (0.34960611626526156, 0.5991493697454252, 0.6827206123863477, 0.7135417368087881, 0.3952561866719522, 0.4843137959185453)]
negatives += [(0.39033008152164445, 0.6514517694879707, 0.7556896053754729, 0.7930582761883025, 0.5226392310703627, 0.5359335427991068), (0.40333926505738193, 0.6562787952039424, 0.7556896053754729, 0.790994062113376, 0.517442666949921, 0.5331459134208651), (0.39814578556860747, 0.6771903669094376, 0.7556896053754729, 0.7833292733785799, 0.52785767219746, 0.5442019124264121), (0.39763827002061003, 0.655695559161736, 0.7515747116671027, 0.7930582761883025, 0.5036195079023206, 0.5523962842906512), (0.40280261975965925, 0.6653723136650809, 0.7515747116671027, 0.790994062113376, 0.5149334203431104, 0.5421294021854721), (0.4037559953378462, 0.6815859437045438, 0.7515747116671027, 0.7833292733785799, 0.5068895036478283, 0.5580146084707039), (0.40108452182292104, 0.6622612868523438, 0.7641785002598394, 0.7930582761883025, 0.5319280302533274, 0.5438876926751346), (0.4172745388717282, 0.6716979098045073, 0.7641785002598394, 0.790994062113376, 0.54136923065617, 0.5355453655845787), (0.41943847722257577, 0.6861016489878905, 0.7641785002598394, 0.7833292733785799, 0.543857406755789, 0.5460750941343138)]
negatives += [(0.3283528765532245, 0.6331335867492184, 0.668343867188534, 0.7432706444625632, 0.45193161693451317, 0.4417382114214627), (0.34989109854299294, 0.6205028123475594, 0.668343867188534, 0.7354743878758024, 0.46548661870303365, 0.4085055166336881), (0.30657157617487324, 0.6255602526021121, 0.668343867188534, 0.7427836890339116, 0.4642080298161604, 0.3932963348812195), (0.35046990968893393, 0.6623382118195669, 0.6505436778839966, 0.7432706444625632, 0.4251817704492928, 0.4704710320949053), (0.351589599021357, 0.6559891668577182, 0.6505436778839966, 0.7354743878758024, 0.4036050888902227, 0.43289772870088267), (0.3202730991324095, 0.655501544843628, 0.6505436778839966, 0.7427836890339116, 0.3945768253437363, 0.4270565037860356), (0.4027208449156625, 0.6653756207493204, 0.6854229483444723, 0.7432706444625632, 0.486704169413551, 0.4830596905432732), (0.37692725610551353, 0.668858416265488, 0.6854229483444723, 0.7354743878758024, 0.4753854677992823, 0.45011110998650383), (0.3648731938768817, 0.6639422690851884, 0.6854229483444723, 0.7427836890339116, 0.45854242547675117, 0.4404808832107225)]
negatives += [(0.3654279013080834, 0.6660579050783773, 0.7017120678707036, 0.7348137555143053, 0.4847031198379437, 0.5136122430100878), (0.42720841266981746, 0.6901090507169659, 0.7017120678707036, 0.7124026798147473, 0.5002966241231913, 0.495075627663467), (0.3818969882599459, 0.6799824882301734, 0.7017120678707036, 0.7350654022122209, 0.5330072694864986, 0.4849088816402333), (0.41166419412942507, 0.6895549714279342, 0.6965397386978371, 0.7348137555143053, 0.526597466577621, 0.5101127853361852), (0.4483409716822943, 0.6887921525345091, 0.6965397386978371, 0.7124026798147473, 0.522569378980635, 0.4870386232527702), (0.37092315558952743, 0.678038959160104, 0.6965397386978371, 0.7350654022122209, 0.5506880320495996, 0.4705340152648662), (0.4057115217312832, 0.6934387680214282, 0.7226157892354608, 0.7348137555143053, 0.5328701692569688, 0.5145421346551402), (0.41645559234062657, 0.703521849390492, 0.7226157892354608, 0.7124026798147473, 0.5373656753696382, 0.5092590125448867), (0.3636849348029665, 0.6826154221011572, 0.7226157892354608, 0.7350654022122209, 0.5693486854654457, 0.49119539782428623)]
negatives += [(0.3944515998861677, 0.6579149870982011, 0.7411065250980304, 0.7410156088435996, 0.5046349818517194, 0.49294484125208704), (0.404675140034431, 0.6603285584921474, 0.7411065250980304, 0.7355308165680117, 0.5081810162669699, 0.48676049364134105), (0.3690546679392259, 0.6639333043017207, 0.7411065250980304, 0.7586889487137669, 0.5157005289298061, 0.4798437787782919), (0.41842390676097807, 0.6521171386891563, 0.8261453701278594, 0.7410156088435996, 0.5378466666967562, 0.5155922538171596), (0.4008857458842705, 0.6546452738876593, 0.8261453701278594, 0.7355308165680117, 0.5447471743476499, 0.5028139704708858), (0.39343507061668354, 0.6825575707466637, 0.8261453701278594, 0.7586889487137669, 0.5602917314192487, 0.5157227536691779), (0.4091939676412506, 0.6432365806119933, 0.8364946555349619, 0.7410156088435996, 0.5334077671091626, 0.5044252566449191), (0.41811130527773527, 0.6592862702324609, 0.8364946555349619, 0.7355308165680117, 0.5469466918752985, 0.4949772820949071), (0.39343507061668354, 0.6834685184199699, 0.8364946555349619, 0.7586889487137669, 0.5689448855724417, 0.5098926792682733)]
negatives += [(0.47702502927458573, 0.7034001183103311, 0.7440800469794578, 0.7847725743451999, 0.5337920288576221, 0.6070739661280741), (0.4978813559322034, 0.7094002304471917, 0.7440800469794578, 0.7254586098301649, 0.5272276693714056, 0.56020267411333), (0.4854840996970214, 0.7068732277304828, 0.7440800469794578, 0.7484790057970322, 0.5471356779062629, 0.5739303525717048), (0.44333992955880047, 0.7112391116007651, 0.7420729249905863, 0.7847725743451999, 0.5585719561939017, 0.5842481946234597), (0.482983096290473, 0.700334748503045, 0.7420729249905863, 0.7254586098301649, 0.5361676248207992, 0.5474404462894596), (0.4791843710748667, 0.7113738788016126, 0.7420729249905863, 0.7484790057970322, 0.5734282889353697, 0.5617295545307524), (0.4906842814809256, 0.7028083776935735, 0.7323146069871628, 0.7847725743451999, 0.5440645979878727, 0.6143187722286433), (0.4989791956686232, 0.694290756868425, 0.7323146069871628, 0.7254586098301649, 0.5283235795156163, 0.5679499530222025), (0.5010405131422097, 0.7147644125565928, 0.7323146069871628, 0.7484790057970322, 0.5595303881645917, 0.5760415864991724)]
negatives += [(0.2762655229193245, 0.5853368370846144, 0.7027467944112618, 0.6880864628082014, 0.3820263347231334, 0.35020938649884503), (0.28782486779428706, 0.559765836060737, 0.7027467944112618, 0.698875869229562, 0.3601269775620649, 0.3646991795271979), (0.30429505828837977, 0.5645736652371477, 0.7027467944112618, 0.7015757432670715, 0.37021078474514335, 0.3775429812933726), (0.3356046329997356, 0.6267762878299717, 0.7548116103247172, 0.6880864628082014, 0.4603409968669914, 0.37274742925487453), (0.32174174850188675, 0.5905338848580522, 0.7548116103247172, 0.698875869229562, 0.4275810725583226, 0.388375756738156), (0.31924952082181896, 0.6097444956130612, 0.7548116103247172, 0.7015757432670715, 0.44533552593531867, 0.4109610376234346), (0.32851194926603733, 0.641456993502449, 0.7520529463912045, 0.6880864628082014, 0.44553433147334315, 0.37783084090880265), (0.3515451125242305, 0.5942385251447149, 0.7520529463912045, 0.698875869229562, 0.4257086385963309, 0.384693464412982), (0.33380098229228317, 0.6214320143797579, 0.7520529463912045, 0.7015757432670715, 0.436752431885496, 0.4120435669434142)]
negatives += [(0.3090739747978402, 0.5832328528322881, 0.7084116158505713, 0.69950674043549, 0.3809275124913098, 0.4015637119418045), (0.27770269255467944, 0.5968608111411451, 0.7084116158505713, 0.6880543181144262, 0.3836856853650598, 0.38174452590700525), (0.28867513459481287, 0.5857407375577074, 0.7084116158505713, 0.6786681117483413, 0.37818959236562516, 0.3985083006461292), (0.32112037822392214, 0.6253341918248344, 0.6682986432544882, 0.69950674043549, 0.38590768305456224, 0.4197943803668199), (0.2863792023354505, 0.6190992918447296, 0.6682986432544882, 0.6880543181144262, 0.3860107776342906, 0.3977947224839735), (0.2650683553724467, 0.617772448489239, 0.6682986432544882, 0.6786681117483413, 0.36933972753791205, 0.4038022428176066), (0.3414584203033404, 0.6183739449064667, 0.6954486466959, 0.69950674043549, 0.42002835524119203, 0.4114277559564698), (0.28593138470052, 0.6225384578073317, 0.6954486466959, 0.6880543181144262, 0.4175244275063076, 0.3956412972230356), (0.28724626484371674, 0.6227931584637963, 0.6954486466959, 0.6786681117483413, 0.4103519025017904, 0.4007559563117123)]

positives += [(0.4442851700029181, 0.742997255724192, 0.6505308571216045, 0.6818134506514194, 0.5229518836332081, 0.5540665323253589), (0.4318181818181818, 0.7783525711027953, 0.6505308571216045, 0.666728739382454, 0.54715945278755, 0.5182412652488991), (0.5482027182408888, 0.7862490140646836, 0.6818134506514194, 0.666728739382454, 0.5968394517990914, 0.547334916244327), (0.524042327405426, 0.8115477189001049, 0.6658273234290748, 0.6350389446613123, 0.5647609946881205, 0.5570195585448026), (0.5220905801127945, 0.7852320133907348, 0.6658273234290748, 0.6719191974765684, 0.5629472953313411, 0.5678330573192854), (0.6026161354020451, 0.8088972070103603, 0.6350389446613123, 0.6719191974765684, 0.5720825132771522, 0.5810426866446388)]
negatives +=[(0.31037611591959413, 0.6109684484987469, 0.6505308571216045, 0.6658273234290748, 0.4100009347274587, 0.42560277789377526), (0.2981471553633822, 0.621330668784763, 0.6505308571216045, 0.6350389446613123, 0.4125822660348969, 0.428362106807302), (0.2970367337946374, 0.596650303966884, 0.6505308571216045, 0.6719191974765684, 0.38336257630445636, 0.4367246016063422), (0.3266597416676063, 0.6325004358707408, 0.6818134506514194, 0.6658273234290748, 0.4259082907847728, 0.4161179522654946), (0.29468213524642006, 0.6019664521624949, 0.6818134506514194, 0.6350389446613123, 0.41010427205299055, 0.39805186318377433), (0.2852441466996468, 0.5964546593323808, 0.6818134506514194, 0.6719191974765684, 0.3872062078249016, 0.4036763334510208), (0.34689095308660517, 0.6476036429766973, 0.666728739382454, 0.6658273234290748, 0.4195835943037265, 0.4399272998896557), (0.3149916274178106, 0.6487257753661454, 0.666728739382454, 0.6350389446613123, 0.4244100881640592, 0.4320204831690888), (0.30374942834366875, 0.6111249555231956, 0.666728739382454, 0.6719191974765684, 0.3799274277712623, 0.42177444342475945)]

positives+=[(0.6319062870042959, 0.8456141911130759, 0.7388506292752318, 0.7035098220068043, 0.6141655239298296, 0.6822413889610424), (0.6003109726540811, 0.8297811535739115, 0.7388506292752318, 0.7260736858772048, 0.6437870121062902, 0.6622644893730082), (0.7194444444444443, 0.8592275245347507, 0.7035098220068043, 0.7260736858772048, 0.6807313685997458, 0.6433606167723585), (0.6232053975448311, 0.8510598189625165, 0.8181188321959847, 0.8020673923747481, 0.7216460197896386, 0.7537569044189728), (0.6420620188025994, 0.8638320453854104, 0.8181188321959847, 0.8101401896241964, 0.7332140890314155, 0.7658084441457989), (0.6802844505392147, 0.8651074262778549, 0.8020673923747481, 0.8101401896241964, 0.7409964096277802, 0.7474794793126532)]
negatives+=[(0.38933280308343177, 0.6330762984333114, 0.7388506292752318, 0.8181188321959847, 0.45088314724298434, 0.5199275992730417), (0.36086255799893274, 0.66287658437751, 0.7388506292752318, 0.8020673923747481, 0.4365560956104078, 0.5338172510919154), (0.3771498085012205, 0.6582475329821408, 0.7388506292752318, 0.8101401896241964, 0.42255480804028434, 0.5362573722401089), (0.3876481102077891, 0.673149531368374, 0.7035098220068043, 0.8181188321959847, 0.47485982574520913, 0.5249043505138467), (0.3466833001425457, 0.6779478240616951, 0.7035098220068043, 0.8020673923747481, 0.4553439473666, 0.5347896381113385), (0.3679116486137106, 0.695957729578629, 0.7035098220068043, 0.8101401896241964, 0.4729352803780984, 0.5337664218705704), (0.34723691725176475, 0.633868517070092, 0.7260736858772048, 0.8181188321959847, 0.4356838901212294, 0.5117685465009987), (0.3481972010165306, 0.6545979514987713, 0.7260736858772048, 0.8020673923747481, 0.4304518115772259, 0.5339040466048007), (0.36195356523535094, 0.6824648867969668, 0.7260736858772048, 0.8101401896241964, 0.430154269885408, 0.5470604464869576)]

positives+=[(0.5431753471017444, 0.7824738596126067, 0.7360861229527417, 0.6863552067445612, 0.6109861922909682, 0.597664193437416), (0.5965219742602734, 0.7851510612131345, 0.7360861229527417, 0.7269530372631313, 0.6371860760115452, 0.6241960356334815), (0.6138104270501384, 0.807680164368931, 0.6863552067445612, 0.7269530372631313, 0.6317517060840191, 0.6038682211389931), (0.5318114743523656, 0.7683560245752385, 0.6457074498170093, 0.6534572637941037, 0.5301127841861153, 0.5269909877332668), (0.5331353250990353, 0.7637795437216633, 0.6457074498170093, 0.6690815792225278, 0.5466988052125115, 0.5552592000000476), (0.6359523031053804, 0.8361792334516351, 0.6534572637941037, 0.6690815792225278, 0.5860707692236501, 0.5763293310914834)]
negatives+=[(0.38145924296025024, 0.6827032410082307, 0.7360861229527417, 0.6457074498170093, 0.4854064543713841, 0.4600850030031419), (0.37726587388355404, 0.7121376992815736, 0.7360861229527417, 0.6534572637941037, 0.5029037433822641, 0.47787892018787637), (0.381570084246582, 0.7014302387442004, 0.7360861229527417, 0.6690815792225278, 0.4762086301004103, 0.4766372421323133), (0.35227458401244094, 0.6652906484353056, 0.6863552067445612, 0.6457074498170093, 0.4573833739253756, 0.4303670388057625), (0.36097990460502133, 0.7103502495337177, 0.6863552067445612, 0.6534572637941037, 0.4755549814204485, 0.4459097830518484), (0.3510507952676081, 0.6746282909511799, 0.6863552067445612, 0.6690815792225278, 0.47938820201517673, 0.44789996823339573), (0.38427615860481756, 0.7074792605436004, 0.7269530372631313, 0.6457074498170093, 0.48768278442594704, 0.4635605133450403), (0.3800721233721607, 0.7210384100378936, 0.7269530372631313, 0.6534572637941037, 0.4912398435522825, 0.46705668272268847), (0.3636405261167026, 0.6869660077999987, 0.7269530372631313, 0.6690815792225278, 0.49157548051195044, 0.4672914705063213)]

positives+=[(0.6160871452807076, 0.8682828001649378, 0.7568698041781475, 0.7455051543444278, 0.7133068784392622, 0.6927112630518563), (0.6685069705346147, 0.8694380616771994, 0.7568698041781475, 0.7532347431146154, 0.7224964588219209, 0.7009644673427511), (0.6373397477596188, 0.8906560024714643, 0.7455051543444278, 0.7532347431146154, 0.697765305291518, 0.7026104381624491), (0.5495892006620626, 0.8114778945299433, 0.711955977722053, 0.6961780163040019, 0.5900300672161252, 0.6201292924257921), (0.5163713345578144, 0.8322112560888748, 0.711955977722053, 0.6783251299242001, 0.5916956257403038, 0.6205464222235227), (0.6069524907639389, 0.8077837545610538, 0.6961780163040019, 0.6783251299242001, 0.589736047948728, 0.6039031359723037)]
negatives+=[(0.3610147361711488, 0.6780609792581904, 0.7568698041781475, 0.711955977722053, 0.47256154313927373, 0.4421783203365069), (0.3653776103508233, 0.6793705639346749, 0.7568698041781475, 0.6961780163040019, 0.46145738698203, 0.4713654473101019), (0.36536762815621626, 0.6684728881395721, 0.7568698041781475, 0.6783251299242001, 0.4677860364853912, 0.45440193793784056), (0.36493289960410585, 0.6946253924776802, 0.7455051543444278, 0.711955977722053, 0.4940302830302791, 0.45224856588688367), (0.38739989990482654, 0.6827675753723725, 0.7455051543444278, 0.6961780163040019, 0.48458061390709334, 0.4782990250325671), (0.37578118062633836, 0.6786871221694571, 0.7455051543444278, 0.6783251299242001, 0.4802008462262233, 0.47699637484132673), (0.36076139339981217, 0.6808904769704218, 0.7532347431146154, 0.711955977722053, 0.4847233210052422, 0.4572464826108306), (0.3781612489930358, 0.676817886614782, 0.7532347431146154, 0.6961780163040019, 0.47921333040642905, 0.4921646164287879), (0.3472986092320741, 0.681280322513274, 0.7532347431146154, 0.6783251299242001, 0.46901407287705643, 0.4753424108046161)]

positives+=[(0.6766766479747167, 0.8372477071341748, 0.8022587080925303, 0.7400744202850675, 0.6903581609957491, 0.7237011627554807), (0.6756017042491915, 0.8521048782471277, 0.8022587080925303, 0.7655104126989158, 0.6929733886926592, 0.7030230982141933), (0.8394287238042243, 0.8992208758814201, 0.7400744202850675, 0.7655104126989158, 0.7203876813147444, 0.6915158518011085), (0.5671172870528557, 0.8034654991900193, 0.6990666767109764, 0.6843693430518523, 0.6049759218314941, 0.600503680617675), (0.5731100531183643, 0.8087992051693527, 0.6990666767109764, 0.7044427716167913, 0.6392496392496392, 0.6008068723507012), (0.6951433537646937, 0.8790760657687038, 0.6843693430518523, 0.7044427716167913, 0.6507706823112863, 0.6318803009344067)]
negatives+=[(0.4035808281607403, 0.6544022900602624, 0.8022587080925303, 0.6990666767109764, 0.4595077119809564, 0.5678142680915894), (0.4231446921146601, 0.6406572807193469, 0.8022587080925303, 0.6843693430518523, 0.4396745042720337, 0.5498767494372384), (0.4077379474080371, 0.6691378463747572, 0.8022587080925303, 0.7044427716167913, 0.4912155222756439, 0.5200127623812135), (0.3831270477066633, 0.6545334372478208, 0.7400744202850675, 0.6990666767109764, 0.4461709782088478, 0.5233370011013774), (0.42753421597132407, 0.6486462669016981, 0.7400744202850675, 0.6843693430518523, 0.43877325487538976, 0.5251079880747709), (0.390656405034322, 0.6731649494861925, 0.7400744202850675, 0.7044427716167913, 0.4729443775719616, 0.4998653947946211), (0.3792490378612998, 0.65547848573505, 0.7655104126989158, 0.6990666767109764, 0.4447779335992184, 0.5075289750613623), (0.4105628732724124, 0.6375431783762741, 0.7655104126989158, 0.6843693430518523, 0.43736159263672686, 0.5094263494203135), (0.39166777163372696, 0.6612006216456805, 0.7655104126989158, 0.7044427716167913, 0.4672889930791015, 0.49226200090232675)]

positives+=[(0.6286678302660923, 0.8149827572237496, 0.6521513473199176, 0.6697493001647489, 0.5811678019531402, 0.5875792446018399), (0.6032819311128859, 0.7986099518245459, 0.6521513473199176, 0.6721252864417377, 0.5626562083973725, 0.5779138127783416), (0.7957686312343533, 0.9002361417574362, 0.6697493001647489, 0.6721252864417377, 0.6327789784839454, 0.6269709199589991), (0.7909223438285486, 0.8590117152283047, 0.6544071800750416, 0.6618830495357102, 0.6273344273328973, 0.6069903107613609), (0.7826692411103378, 0.8761565100720489, 0.6544071800750416, 0.6373939516738217, 0.615793972749408, 0.5918910492996355), (0.9173553719008265, 0.9234342024964637, 0.6618830495357102, 0.6373939516738217, 0.6314647056117397, 0.6305617980844668)]
negatives+=[(0.4045035742293485, 0.6566403197595304, 0.6521513473199176, 0.6544071800750416, 0.4506079686418862, 0.40583400087195287), (0.40956102914035164, 0.6454221520357951, 0.6521513473199176, 0.6618830495357102, 0.45249226617835764, 0.4063926164163), (0.4050603584904577, 0.6760506499599912, 0.6521513473199176, 0.6373939516738217, 0.4468874593360844, 0.4088668484797173), (0.45843981620031576, 0.6645816208410403, 0.6697493001647489, 0.6544071800750416, 0.4602891769945145, 0.40293651357487276), (0.45458480742674945, 0.6685364273401794, 0.6697493001647489, 0.6618830495357102, 0.47604180810201563, 0.39989389440828704), (0.46355687599438267, 0.683138835799194, 0.6697493001647489, 0.6373939516738217, 0.4673196564914116, 0.4022920586925946), (0.45092444085363925, 0.6697764220969542, 0.6721252864417377, 0.6544071800750416, 0.46792737436674653, 0.41011024111655986), (0.4620811745670096, 0.6633288762913129, 0.6721252864417377, 0.6618830495357102, 0.47012260779569803, 0.40200287789358685), (0.45305027213247523, 0.6721921022917271, 0.6721252864417377, 0.6373939516738217, 0.46714452073298796, 0.3982863643845552)]

positives+= [(0.5953573692589823, 0.7608687539315565, 0.6295653809678796, 0.6164198071445679, 0.528008888288947, 0.5393572830949706), (0.6622406925886923, 0.8001654006515511, 0.6295653809678796, 0.6264944710413033, 0.5510070436018294, 0.5835447035500534), (0.6867912567899804, 0.8082392678574459, 0.6164198071445679, 0.6264944710413033, 0.5662200652392857, 0.5526195331746482), (0.5144990737851642, 0.7599065502419774, 0.609546275796441, 0.6160525798218204, 0.5053325199677045, 0.5128256838687564), (0.5068377463604778, 0.7921842229601801, 0.609546275796441, 0.6292330711529417, 0.5159261959170593, 0.520858637533051), (0.5533002844424411, 0.7998500591071034, 0.6160525798218204, 0.6292330711529417, 0.5287210667459417, 0.5268428331850686)]
negatives+= [(0.27998072023796217, 0.5682955908012404, 0.6295653809678796, 0.609546275796441, 0.3519244049506833, 0.31086806218008917), (0.2341254973798407, 0.5638619547033764, 0.6295653809678796, 0.6160525798218204, 0.3386733701129343, 0.26409138506816515), (0.2814263814419536, 0.5643484437951582, 0.6295653809678796, 0.6292330711529417, 0.35061440868304167, 0.3177461031476668), (0.2821348490826109, 0.5612635389469774, 0.6164198071445679, 0.609546275796441, 0.3489621489465027, 0.28802490990275936), (0.24288959081596867, 0.5764364776669844, 0.6164198071445679, 0.6160525798218204, 0.3566694274791388, 0.2744553386236508), (0.291961103759477, 0.5796558361324864, 0.6164198071445679, 0.6292330711529417, 0.3526153168300309, 0.32916112097250205), (0.2930259625531399, 0.5952568425994088, 0.6264944710413033, 0.609546275796441, 0.3754999777281689, 0.3235614985622319), (0.29560810810810817, 0.5983880212913875, 0.6264944710413033, 0.6160525798218204, 0.37578474845254917, 0.2984680218769845), (0.27580411732146143, 0.6097887593276307, 0.6264944710413033, 0.6292330711529417, 0.3698901102945221, 0.33797001170748764)]

positives+= [(0.5668461077987654, 0.8130467212134097, 0.7644827967340168, 0.7657128801491087, 0.705465976595776, 0.6524449774285741), (0.5555771576927583, 0.8214393826017035, 0.7644827967340168, 0.744211427855451, 0.6873451205125596, 0.6410253845332557), (0.6388131982927963, 0.8623757036683765, 0.7657128801491087, 0.744211427855451, 0.6835990727814749, 0.6865323500037992), (0.4904686742053749, 0.8119248531300102, 0.7088321124313411, 0.6554428436327089, 0.6093837696720121, 0.5723482656580631), (0.510383678267777, 0.8178848804992307, 0.7088321124313411, 0.7203973948069357, 0.6222468664121362, 0.604761039580966), (0.5630405634170392, 0.8224052114080993, 0.6554428436327089, 0.7203973948069357, 0.5845102052184675, 0.6287203177975124)]
negatives+= [(0.390187700063878, 0.6953975131665625, 0.7644827967340168, 0.7088321124313411, 0.5161858861325846, 0.5103228411736304), (0.3088023458348626, 0.7013579018770322, 0.7644827967340168, 0.6554428436327089, 0.5227720820513442, 0.45742649464351315), (0.35205774495952513, 0.7034183760126878, 0.7644827967340168, 0.7203973948069357, 0.5135982503167623, 0.5263418830814294), (0.3548505750402986, 0.6993471250751789, 0.7657128801491087, 0.7088321124313411, 0.4819453716288126, 0.5346200601579933), (0.36669668155815677, 0.7173184515944149, 0.7657128801491087, 0.6554428436327089, 0.49758434728428175, 0.46399017227039857), (0.34296278002946246, 0.7000785364592145, 0.7657128801491087, 0.7203973948069357, 0.5008131228097047, 0.5285561498994052), (0.3745667336490094, 0.700950957896615, 0.744211427855451, 0.7088321124313411, 0.4858922828817821, 0.5254042283562278), (0.3565265916992998, 0.6991177139289813, 0.744211427855451, 0.6554428436327089, 0.5105209504361143, 0.47316991416591003), (0.3680644306729428, 0.7087334783356849, 0.744211427855451, 0.7203973948069357, 0.5104538095426173, 0.516570731068887)]

fnames = [f for f in os.listdir('.') if re.match(r'(res[0-9]+\.[0-9]*\.dat)', f) and os.stat(f)[6] != 0]

for fname in fnames:
    with open(fname,'r') as f:
        for x in f:
            sa1, sa2, pos, neg = x.split("\t")
            pos = json.loads(pos)
            neg = json.loads(neg)
            positives += pos
            negatives += neg


def calculate_tp_fp(threshold):
    tp, fp = 0.0, 0.0

    for (a1_a2, ca1_ca2, a1_ca1, a2_ca2, a1_ca2, a2_ca1) in positives:
        res = ((a2_ca1 / a1_ca1) + (a1_ca2 / a2_ca2)) / 2
        #res = max( (a2_ca1 / a1_ca1) , (a1_ca2 / a2_ca2) )
        res = 1 - ((abs(a2_ca1 - a1_ca1) + abs(a1_ca2 - a2_ca2)) / 2)
        if res >= threshold:
            tp += 1

    for (a1_a2, ca1_ca2, a1_ca1, a2_ca2, a1_ca2, a2_ca1) in negatives:
        res = ((a2_ca1 / a1_ca1) + (a1_ca2 / a2_ca2)) / 2
        #res = max( (a2_ca1 / a1_ca1) , (a1_ca2 / a2_ca2) )
        res = 1 - ((abs(a2_ca1 - a1_ca1) + abs(a1_ca2 - a2_ca2)) / 2)
        if res >= threshold:
            fp += 1

    return tp / len(positives), fp / len(negatives)


if __name__ == "__main__":
    for threshold in THRESHOLDS:
        tp_rate, fp_rate = calculate_tp_fp(threshold)
        #print "{threshold}\n\tTP RATE : {tp_rate}\n\tFP RATE : {fp_rate}".format(**locals())
        print "{threshold}\t{tp_rate}\t{fp_rate}".format(**locals())
        
    print "{0} total positive, {1} total negative".format(len(positives), len(negatives))
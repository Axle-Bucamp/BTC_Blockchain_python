from bcTools.Curve import Curve
from bcTools.ElepticPoint import ElepticPoint
from bcTools.PublicKey import PublicKey
from bcTools.Signature import *
from bcTools.Tx import *
from bcTools.sha import sha256
from bcTools.Block import Block
from bcTools.Blockchain import Blockchain

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # todo:
    # rajouter un decode transaction
    # vérifier clef public
    # ajout vérification des wallet
    # voir merkle tree
    # simuler le réseaux voir faire un cluster dans l'optimal

    # implementer les outils de la bibliothèque : https://github.com/primal100/pybitcointools
    # examiner les propositions de code : https://github.com/concept-inversion/blockchain-simulator

    # une blockchain est static et donne aux le broadcast du dernier block (simule le réseaux)
    # sinon chaque noeud s'enregistre dans la blockchain via le partage d'un fichier ou de socket simulé entre eux

    # chaques noeud execute la preuve et enregistre des transactions
    # le block gagnant publie les transaction
    # on laisse un temps de validation du block auprès des noeuds (consensus)
    # on valide la preuves ou le changement de block
    # on enregistre les résultats
    # etc

    print("here will be some code to test out the whole solution")

    # liens de vérification des transaction :
    # https://www.blockchain.com/explorer/addresses/btc-testnet/mnNcaVkC35ezZSgvn8fhXEa9QTHSUtPfzQ
    # https://live.blockcypher.com/btc/decodetx/

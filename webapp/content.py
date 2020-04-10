from dataclasses import dataclass
from flask import Markup


@dataclass
class ContentEn:
    days_since_lockdown_started: int
    glasses_sold: int

    @property
    def title(self):
        return 'A Glass of Wine May Help'

    @property
    def isolation_text(self):
        return Markup(f"DAY <span class='has-text-weight-bold'> {self.days_since_lockdown_started} </span>OF ISOLATION")

    @property
    def well_done(self):
        return Markup(
            f'Well done everybody, yesterday we bought <span class="has-text-weight-bold">{self.glasses_sold} glasses </span> of wine from SAQ online!')

    @property
    def what_is_quebec_drinking(self):
        return "What is Quebec drinking?"

    @property
    def recommendations(self):
        return '''
        We've been looking at the the stock in SAQ, to see how people have
                been following Legault's recommendations.'''

    @property
    def wine_types(self):
        return "Are we guzzling more red, white, or rosé?"

    @property
    def trending(self):
        return "Well! Here are the trending bottles in Quebec"

    @property
    def bottle_label(self):
        return "bottles today"

    @property
    def map_blurb(self):
        return "We might be isolated, but we're drinking wines from all over!"

    @property
    def since_we_started_drinking(self):
        return "Since we started drinking our wine alone"

    @property
    def prediction(self):
        return """It takes a couple of weeks for the effects of social distancing to become apparent.
                    We can hope to see the growth of new cases slowing around April 7th."""

    @property
    def relative_to_world(self):
        return "Here's how we're doing relative to everyone else"

    @property
    def internationally(self):
        return '''Across the world, people are locked away drinking their local tipples and trying to keep COVID-19
                    under control. Our friends in Italy seem to have turned a corner: we'll raise a glass of
                     Valpolicella to that!'''

    @property
    def stay_home(self):
        return "Stay home, open a bottle, and know that Quebec drinks with you!"

    @property
    def footer(self):
        return Markup("""
                <strong>A Glass of Wine May Help </strong> is made by
                <a href=""> Archy de Berker </a> and <a href=""> Claudel Rheault</a> with help from
                <a href=""> Stephanie Willis</a>
                <p class="is-size-9"> COVID-19 data refreshed daily from
                <a href={{data_citation}}> COVID-19 Canada Open Data Working Group </a>
            and <a href={{case_api_citation}}> the Coronavirus Tracker API </a></p>
            """)


@dataclass
class ContentFr:
    days_since_lockdown_started: int
    glasses_sold: int

    @property
    def title(self):
        return 'Un Verre de Vin Peut Aider'

    @property
    def isolation_text(self):
        return Markup(f"JOUR <span class='has-text-weight-bold'> {self.days_since_lockdown_started} </span> DE"
                      f" DISTANCIATION SOCIALE")

    @property
    def well_done(self):
        return Markup(
            f'Bravo à tous, hier seulement nous avons cumulé un total de'
            f' <span class="has-text-weight-bold">{self.glasses_sold} verres </span> de vin sur le site de la SAQ!')

    @property
    def what_is_quebec_drinking(self):
        return "Le Québec boit quoi?"

    @property
    def recommendations(self):
        return '''
            Nous avons analysé l’inventaire en ligne de la SAQ, histoire de comprendre comment la 
            population suit les recommandations de Legault.
            '''

    @property
    def wine_types(self):
        return "Sommes nous plus rouge, blanc ou rosé?"

    @property
    def trending(self):
        return "Voici donc les bouteilles qui sont préférées en ce moment!"

    @property
    def bottle_label(self):
        return "bouteilles aujourd'hui"

    @property
    def map_blurb(self):
        return "Malgré l’isolation, nous sommes connectés au reste du monde par nos choix de vin! "

    @property
    def since_we_started_drinking(self):
        return "Depuis que nous dégustons notre verre de vin seul"

    @property
    def prediction(self):
        return """
        Plusieurs semaines doivent s’écouler avant que les impacts de la distanciation sociale soient visibles. 
        Les effets plus tangibles devraient se faire sentir aux alentours de la mi avril. 
        """

    @property
    def relative_to_world(self):
        return "Comment on se situe comparativement à ailleurs"

    @property
    def internationally(self):
        return '''Autour du monde, plusieurs se retrouvent tout comme nous en confinement à la maison, 
        dans un effort global pour réduire la progression de la pandémie. Nos amis en Italie semblent 
        avoir réussi à tourner la pente: levons notre verre de Valpolicella à leurs efforts! 
        '''

    @property
    def stay_home(self):
        return '''
                Restez à la maison, ouvrez une bonne bouteille, et dites vous que tout le Québec lève son verre ensemble! 
                '''

    @property
    def footer(self):
        return Markup("""
                <strong>Un Verre de Vin Peut Aider </strong> est fait par
                <a href=""> Archy de Berker </a> etc <a href=""> Claudel Rheault</a> avec l'aide de
                <a href=""> Stephanie Willis</a>
                <p class="is-size-9"> Données de COVID-19 rafraîchie chaque jour de
                <a href={{data_citation}}> COVID-19 Canada Open Data Working Group </a>
            et <a href={{case_api_citation}}> the Coronavirus Tracker API </a></p>
            """)

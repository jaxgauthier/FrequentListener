from manim import *

class SquareToCircle(Scene): 
    def construct(self):
        # Create axes with pi-based x labels
        graph = Axes(
            x_range=[0, 1, 0.1],
            y_range=[-2, 2, 0.5],
            axis_config={"color": BLUE},
        )

        # Create pi labels
        labels = [
            (0, "0"),
            (1/2, "1/2"),
            (1, "1"),
            (3/2, "3/2"),
            (2, "2")
        ]
        
        # Add labels to graph
        for x, tex in labels:
            label = MathTex(tex)
            label.scale(0.7)
            label.next_to(graph.c2p(x, 0), DOWN)
            graph.add(label)

        # Create and plot sine wave
        a = 10
        sine_wave = graph.plot(lambda x: np.sin(2*np.pi*a*x), color=RED)
        frequency = a
        period = 1 / frequency
        self.add(MathTex(f"Frequency: {frequency} HZ").to_edge(DOWN).shift(LEFT*2.5))
        self.add(MathTex(f" T = {period} s").to_edge(DOWN).shift(RIGHT*2.5))

        # Animate
        self.play(Create(graph))
        self.play(Create(sine_wave), run_time=2)
        self.wait(5)
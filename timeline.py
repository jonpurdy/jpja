import plotly.offline as poff
import plotly.figure_factory as ff
import datetime

def main():

      df = [dict(Start='2020-09-14', Finish='2020-10-07', Resource="Story", Task="Hookup IAP for"),
      dict(Start='2020-10-05', Finish='2020-10-07', Resource="QAStory", Task="QA Hookup IAP for")]

      generate_timeline(df)

def generate_timeline(df, filename, colors, height):

      if colors == 0:
            colors='Blues'

      today = datetime.datetime.now().strftime("%Y-%m-%d")

      fonts = dict(
              family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen-Sans, Ubuntu, Cantarell, Helvetica Neue, sans-serif",
              size=8,
              color="#444444"
              ),

      fig = ff.create_gantt(df, colors=colors, index_col='Resource', group_tasks=True)

      fig.update_layout(
          autosize=True,
          #width=100,
          height=height,
          paper_bgcolor="White",
      )

      # fig['layout']['annotations'] = annots

      poff.plot(fig, auto_open=False, filename=filename)

if __name__ == '__main__':
      main()
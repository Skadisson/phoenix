from sklearn import pipeline


class SciKitPipeline(pipeline.Pipeline):

    def partial_fit(self, X, y=None, classes=None):
        for i, step in enumerate(self.steps):
            name, est = step
            est_dir = dir(est)
            if "partial_fit" in est_dir:
                try:
                    est.partial_fit(X, y, classes=classes)
                except Exception as e:
                    """ignore"""
            elif "fit_transform" in est_dir:
                est.fit_transform(X, y)
            if i < len(self.steps) - 1:
               X = est.transform(X)
        return self

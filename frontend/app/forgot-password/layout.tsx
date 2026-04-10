export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-md px-4">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-extrabold tracking-tight">
            DIRECTOR <span className="text-accent">HUB</span> PRO
          </h1>
          <p className="mt-2 text-sm text-muted">
            Plataforma para directores deportivos de ciclismo
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}

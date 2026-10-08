import Script from "next/script";

// vercel analytics = no cookies, no banner needed. GA only if NEXT_PUBLIC_GA_ID is set
export default function Analytics() {
  const ga = process.env.NEXT_PUBLIC_GA_ID;
  return (
    <>
      {process.env.VERCEL && <Script src="/_vercel/insights/script.js" strategy="afterInteractive" />}
      {ga && (
        <>
          <Script src={`https://www.googletagmanager.com/gtag/js?id=${ga}`} strategy="afterInteractive" />
          <Script id="ga" strategy="afterInteractive">
            {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','${ga}',{anonymize_ip:true});`}
          </Script>
        </>
      )}
    </>
  );
}
